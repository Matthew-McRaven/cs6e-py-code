import io
from typing import cast, List
from .arguments import Hexadecimal, Decimal, Identifier
from .ir import EmptyLine, ErrorLine, CommentLine, DyadicLine
from .macro import MacroRegistry
from .lexer import Lexer
from .mnemonics import (
    INSTRUCTION_TYPES,
    AddressingMode,
)
from .symbol import SymbolTable, SymbolEntry
import cs6th_ch7.pep10.tokens as tokens
from .types import ArgumentType, ParseTreeNode
from cs6th_ch7.utils.buffer import ParserBuffer

"""
1. argument          ::= HEX | DECIMAL | IDENTIFIER
2. instruction       ::= IDENTIFIER argument COMMA IDENTIFIER
3. line              ::= instruction [COMMENT]
4. statemet          ::= [COMMENT  | [SYMBOL] line] EMPTY
"""


class Parser:
    def __init__(
        self,
        buffer: io.StringIO,
        symbol_table: SymbolTable | None = None,
    ):
        self.lexer = Lexer(buffer)
        self._buffer = ParserBuffer(self.lexer)
        self.symbol_table = symbol_table if symbol_table else SymbolTable()

    def __iter__(self):
        return self

    def __next__(self) -> ParseTreeNode:
        if self._buffer.peek() is None:
            raise StopIteration()
        try:
            return self.statement()
        except SyntaxError as s:
            self._buffer.skip_to_next_line({tokens.Empty})
            return ErrorLine(error=s.msg if s.msg else None)
        except KeyError:
            self._buffer.skip_to_next_line({tokens.Empty})
            return ErrorLine()

    # argument ::= HEX | DECIMAL |  IDENTIFIER
    def argument(self) -> ArgumentType | None:
        if _hex := self._buffer.may_match(tokens.Hex):
            return Hexadecimal(_hex.value)
        elif dec := self._buffer.may_match(tokens.Decimal):
            return Decimal(dec.value)
        elif ident := self._buffer.may_match(tokens.Identifier):
            return Identifier(self.symbol_table.reference(ident.value))
        return None

    # instruction    ::= IDENTIFIER argument COMMA IDENTIFIER
    def instruction(
        self, symbol: SymbolEntry | None = None
    ) -> DyadicLine | None:
        if not (mn := self._buffer.may_match(tokens.Identifier)):
            return None
        mn_str = mn.value.upper()
        if mn_str not in INSTRUCTION_TYPES:
            raise SyntaxError(f"Unrecognized mnemonic: {mn_str}")
        if not (argument := self.argument()):
            raise SyntaxError(f"Missing argument")
        as_int = int(argument)
        try:
            as_int.to_bytes(2, signed=as_int < 0)
        except OverflowError:
            raise SyntaxError("Number too large")

        self._buffer.must_match(tokens.Comma)
        # Check that addressing mode is a valid string and is allowed for the current mnemonic
        addr_str = self._buffer.must_match(tokens.Identifier).value.upper()
        try:
            addr = cast(AddressingMode, AddressingMode[addr_str])
            mn_type = INSTRUCTION_TYPES[mn_str]
            if not mn_type.allows_addressing_mode(addr):
                raise SyntaxError()
        except KeyError:
            raise SyntaxError()

        return DyadicLine(mn_str, argument, addr, sym=symbol)

    # line              ::= instruction [COMMENT]
    def line(self, symbol: SymbolEntry | None = None) -> DyadicLine | None:
        line: ParseTreeNode | None = None
        if instr := self.instruction(symbol=symbol):
            line = instr
        else:
            return None

        if comment := self._buffer.may_match(tokens.Comment):
            line.comment = comment.value
        return line

    # statement         ::= [COMMENT  | [SYMBOL] line] EMPTY
    def statement(self) -> ParseTreeNode:
        line: ParseTreeNode | None = None
        if self._buffer.may_match(tokens.Empty):
            return EmptyLine()
        elif comment := self._buffer.may_match(tokens.Comment):
            line = CommentLine(comment.value)
        elif symbol_token := self._buffer.may_match(tokens.Symbol):
            symbol = self.symbol_table.define(symbol_token.value)
            if (code := self.line(symbol=symbol)) is None:
                message = "Symbol declaration must be followed by instruction"
                raise SyntaxError(message)
            line = code
        elif (code := self.line()) is not None:
            line = code
        else:
            raise SyntaxError()

        self._buffer.must_match(tokens.Empty)

        return line


def parse(
    text: str,
    symbol_table: SymbolTable | None = None,
    macro_registry: MacroRegistry | None = None,
) -> List[ParseTreeNode]:
    # Remove trailing whitespace while insuring input is \n terminated.
    parser = Parser(
        io.StringIO(text.rstrip() + "\n"),
        symbol_table=symbol_table,
    )

    return [line for line in parser]
