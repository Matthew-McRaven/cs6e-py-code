from typing import List, cast, Sequence
import cs6th_ch7.expr.tokens as tokens
from .tokens import Token
from ..pep10.arguments import Decimal, Identifier
from ..pep10.symbol import SymbolTable
from ..pep10.ir import DyadicLine, MonadicLine, ListableLine
from ..pep10.mnemonics import AddressingMode as AM


def expression_string(expression: List[Token]) -> str:
    return " ".join(token.postfix_format() for token in expression)


def plus_ir(symbol_table: SymbolTable) -> List[ListableLine]:
    return [
        DyadicLine(
            "LDWA", Decimal(2), AM.S, symbol_decl=symbol_table.define("plus")
        ),
        DyadicLine("ADDA", Decimal(4), AM.S),
        MonadicLine("RET"),
    ]


def times_ir(symbol_table: SymbolTable) -> List[ListableLine]:
    arg1, arg2, tmp = 6, 4, 0
    return [
        DyadicLine(
            "SUBSP", Decimal(2), AM.I, symbol_decl=symbol_table.define("times")
        ),
        # Initialize accumulation variable to 0
        DyadicLine("LDWA", Decimal(0), AM.I),
        DyadicLine("STWA", Decimal(tmp), AM.S),
        DyadicLine(
            "LDWA",
            Decimal(arg1),
            AM.S,
            symbol_decl=symbol_table.define("b_loop"),
        ),
        DyadicLine("LDWX", Decimal(arg2), AM.S),
        DyadicLine("BREQ", Identifier(symbol_table.reference("e_loop")), AM.I),
        DyadicLine("ANDX", Decimal(1), AM.I),
        DyadicLine("BREQ", Identifier(symbol_table.reference("noadd")), AM.I),
        # Accumulate product
        DyadicLine("ADDA", Decimal(tmp), AM.S),
        DyadicLine("STWA", Decimal(tmp), AM.S),
        DyadicLine("LDWA", Decimal(arg1), AM.S),
        # Shift A/X and write back
        MonadicLine("ASLA", symbol_decl=symbol_table.define("noadd")),
        DyadicLine("STWA", Decimal(arg1), AM.S),
        DyadicLine("LDWX", Decimal(arg2), AM.S),
        MonadicLine("ASRX"),
        DyadicLine("STWX", Decimal(arg2), AM.S),
        DyadicLine("BR", Identifier(symbol_table.reference("b_loop")), AM.I),
        DyadicLine(
            "LDWA",
            Decimal(tmp),
            AM.S,
            symbol_decl=symbol_table.define("e_loop"),
        ),
        DyadicLine("ADDSP", Decimal(2), AM.I),
        MonadicLine("RET"),
    ]


def to_pep10_ir(expression: List[Token]) -> Sequence[ListableLine]:
    symbol_table = SymbolTable()
    ret: List[ListableLine] = []
    for token in expression:
        match type(token):
            case tokens.Decimal:
                casted = cast(Decimal, token)
                ret.append(DyadicLine("SUBSP", Decimal(2), AM.I))
                ret.append(DyadicLine("LDWA", Decimal(casted.value), AM.I))
                ret.append(DyadicLine("STWA", Decimal(0), AM.S))
            case tokens.Plus:
                sym_plus = symbol_table.reference("plus")
                ret.append(DyadicLine("CALL", Identifier(sym_plus), AM.I))
                ret.append(DyadicLine("ADDSP", Decimal(2), AM.I))
                ret.append(DyadicLine("STWA", Decimal(0), AM.S))
            case tokens.Times:
                sym_times = symbol_table.reference("times")
                ret.append(DyadicLine("CALL", Identifier(sym_times), AM.I))
                ret.append(DyadicLine("ADDSP", Decimal(2), AM.I))
                ret.append(DyadicLine("STWA", Decimal(0), AM.S))
    ret.append(DyadicLine("LDWA", Decimal(1), AM.I))
    ret.append(DyadicLine("SCALL", Decimal(0), AM.S))
    ret.append(MonadicLine("RET"))
    ret.extend(plus_ir(symbol_table))
    ret.extend(times_ir(symbol_table))
    return ret
