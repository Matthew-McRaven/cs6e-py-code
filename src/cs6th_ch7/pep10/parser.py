import io
from typing import cast, List
from .arguments import Hexadecimal, Decimal, Identifier
from .ir import IRLine
from .ir import EmptyLine, ErrorLine, CommentLine, DyadicLine
from .lexer import Lexer
from .mnemonics import INSTRUCTION_TYPES, AddressingMode
from .symbol import SymbolTable, SymbolEntry
import cs6th_ch7.pep10.tokens as tokens
from .arguments import ArgumentType
from ..utils.buffer import ParserBuffer

"""
1. argument    ::= HEX | DECIMAL | IDENTIFIER
2. instruction ::= IDENTIFIER argument COMMA IDENTIFIER
3. line        ::= instruction [COMMENT]
4. statement   ::= [COMMENT  | [SYMBOL] line] EMPTY
"""
class Parser:
    def __init__(
        self, buffer: io.StringIO, symbol_table: SymbolTable | None = None
    ):
        self.lexer = Lexer(buffer)
        self._buffer = ParserBuffer(self.lexer)
        self.symbol_table = symbol_table if symbol_table else SymbolTable()

    def __iter__(self):
        return self

    def __next__(self) -> IRLine:
        if self._buffer.peek() is None:
            raise StopIteration()
        try:
            return self.statement()
        except SyntaxError as s:
            self._buffer.skip_to_next_line({tokens.Empty})
            return ErrorLine(comment=s.msg if s.msg else None)
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

    # instruction ::= IDENTIFIER argument COMMA IDENTIFIER
    def instruction(
        self, symbol_entry: SymbolEntry | None
    ) -> DyadicLine | None:
        if not (mn_token := self._buffer.may_match(tokens.Identifier)):
            return None
        mn_str = mn_token.value.upper()

        if mn_str not in INSTRUCTION_TYPES:
            raise SyntaxError(f"Unrecognized mnemonic: {mn_str}")
        if not (arg_ir := self.argument()):
            raise SyntaxError(f"Missing argument")

        try:
            arg_int = int(arg_ir)
            arg_int.to_bytes(2, signed=arg_int < 0)
        except OverflowError:
            raise SyntaxError("Number too large")

        self._buffer.must_match(tokens.Comma)

        addr_str = self._buffer.must_match(tokens.Identifier).value.upper()
        try:
            # Check if addressing mode is valid for this mnemonic
            addr_mode = cast(AddressingMode, AddressingMode[addr_str])
            mn_type = INSTRUCTION_TYPES[mn_str]
            if not mn_type.allows_addressing_mode(addr_mode):
                err = f"Invalid addressing mode {addr_str} for {mn_str}"
                raise SyntaxError(err)
        except KeyError:
            raise SyntaxError(f"Unknown addressing mode: {addr_str}")

        return DyadicLine(mn_str, arg_ir, addr_mode, symbol_decl=symbol_entry)

    # line ::= instruction [COMMENT]
    def line(self, symbol_entry: SymbolEntry | None) -> DyadicLine | None:
        return_ir: DyadicLine | None = None

        if not (return_ir := self.instruction(symbol_entry)):
            return None

        if comment := self._buffer.may_match(tokens.Comment):
            return_ir.comment = comment.value
        return return_ir

    # statement ::= [COMMENT  | [SYMBOL] line] EMPTY
    def statement(self) -> IRLine:
        return_ir: IRLine | None = None
        if self._buffer.may_match(tokens.Empty):
            return EmptyLine()
        elif comment_token := self._buffer.may_match(tokens.Comment):
            return_ir = CommentLine(comment_token.value)
        elif symbol_token := self._buffer.may_match(tokens.Symbol):
            symbol_entry = self.symbol_table.define(symbol_token.value)
            if not (return_ir := self.line(symbol_entry)):
                message = "Symbol declaration must be followed by instruction"
                raise SyntaxError(message)
        elif not (return_ir := self.line(None)):
            raise SyntaxError("Failed to parse line")

        self._buffer.must_match(tokens.Empty)

        return return_ir


def parse(text: str, symbol_table: SymbolTable | None = None) -> List[IRLine]:
    # Ensure input is terminated with a single \n.
    parser = Parser(io.StringIO(text.rstrip() + "\n"), symbol_table)

    return [item for item in parser]
