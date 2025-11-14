import io
from typing import cast
import typing

import pytest

from cs6th_ch7.pep10.arguments import (
    Decimal,
    Hexadecimal,
    Identifier,
    StringConstant,
)
from cs6th_ch7.pep10.ir import (
    CommentLine,
    DyadicLine,
    EmptyLine,
    ErrorLine,
    MonadicLine,
)
from cs6th_ch7.pep10.macro import MacroRegistry
from cs6th_ch7.pep10.mnemonics import AddressingMode
from cs6th_ch7.pep10.parser import Parser, parse


@pytest.mark.skip("Implement in Problem 7.##")
@typing.no_type_check
def test_unary_pass() -> None:
    par = Parser(io.StringIO("RET \n"))
    item: MonadicLine = cast(MonadicLine, next(par))
    assert type(item) is MonadicLine
    assert item.mnemonic == "RET"

    res = parse("caT:NOTA \n")
    item = cast(MonadicLine, res[0])
    assert type(item) is MonadicLine
    assert item.mnemonic == "NOTA"
    assert str(item.symbol_decl) == "caT"


def test_unary_fail() -> None:
    res = parse("RETS \n")
    assert type(res[0]) is ErrorLine

    res = parse("RETS \n")
    assert type(res[0]) is ErrorLine


@pytest.mark.skip("Implement in Problem 7.##")
@typing.no_type_check
def test_macro() -> None:
    mr = MacroRegistry()
    mr.insert("HI", 2, ";WORLD")
    res = parse("@HI 2, 4\n", macro_registry=mr)
    assert type(res[0]) is MacroLine
    item: MacroLine = res[0]
    assert len(item.body) == 1
    assert type(item.body[0]) is CommentLine


def test_nonunary() -> None:
    par = Parser(io.StringIO("BR 10,i \n"))
    item: DyadicLine = cast(DyadicLine, next(par))
    assert type(item) is DyadicLine
    assert item.mnemonic == "BR"
    assert type(item.argument) is Decimal

    ret = parse("cat: BR 0x10,x ;comment\n")
    item = cast(DyadicLine, ret[0])
    assert type(item) is DyadicLine, str(item.source())
    assert str(item.symbol_decl) == "cat"
    assert item.mnemonic == "BR"
    assert type(item.argument) is Hexadecimal
    assert item.comment == "comment"

    ret = parse("cat: BR cat,i")
    item = cast(DyadicLine, ret[0])
    assert type(item) is DyadicLine
    assert str(item.symbol_decl) == "cat"
    assert item.mnemonic == "BR"
    assert type(item.argument) is Identifier
    arg: Identifier = item.argument
    assert str(arg) == "cat"
    assert not arg.symbol.is_undefined()
    assert not arg.symbol.is_multiply_defined()


def test_nonunary_fail() -> None:
    par = Parser(io.StringIO("ADDA 10\n"))
    assert type(next(par)) is ErrorLine

    ret = parse("ADDA 10 ,\n")
    assert type(ret[0]) is ErrorLine

    ret = parse("ADDA 10,cat\n")
    assert type(ret[0]) is ErrorLine

    ret = parse("ADDA cat:,sfx\n")
    assert type(ret[0]) is ErrorLine


@pytest.mark.skip("Implement in Problem 7.##")  # FIGURE ONLY
def test_nonunary_addr_optional() -> None:
    ret = parse("BR 10\n")
    item: DyadicLine = cast(DyadicLine, ret[0])
    assert type(item) is DyadicLine
    assert item.mnemonic == "BR"
    assert type(item.argument) is Decimal
    assert int(item.argument) == 10
    assert item.addressing_mode == AddressingMode.I


def test_nonunary_arg_range() -> None:
    ret = parse("BR 65535, i\n")
    assert not type(ret[0]) is ErrorLine
    ret = parse("BR 65536, i\n")
    assert type(ret[0]) is ErrorLine
    ret = parse("BR -32768, i\n")
    assert not type(ret[0]) is ErrorLine
    ret = parse("BR -32769, i\n")
    assert type(ret[0]) is ErrorLine
    ret = parse("BR 0xFFFF, i\n")
    assert not type(ret[0]) is ErrorLine
    ret = parse("BR 0x10000, i\n")
    assert type(ret[0]) is ErrorLine


def test_comment() -> None:
    par = Parser(io.StringIO("  ;comment \n"))
    item: CommentLine = cast(CommentLine, next(par))
    assert type(item) is CommentLine
    assert item.comment == "comment "


def test_empty() -> None:
    par = Parser(io.StringIO("\n"))
    item: EmptyLine = cast(EmptyLine, next(par))
    assert type(item) is EmptyLine


def test_parser_synchronization() -> None:
    ret = parse("NOPN HELLO CRUEL: WORLD\nNOPN\nRET\n")
    assert len(ret) == 3


@pytest.mark.skip("Implement in Problem 7.##")
@typing.no_type_check
def test_dot_ASCII() -> None:
    ret = parse('cat: .ASCII "Hello World"')
    assert len(ret) == 1
    item: DotASCIINode = cast(DotASCIINode, ret[0])
    assert type(item) is DotASCIINode
    assert str(item.argument) == '"Hello World"'
    assert item.symbol_decl and str(item.symbol_decl) == "cat"
    ret = parse('.ASCII ""')
    item = cast(DotASCIINode, ret[0])
    assert type(item) is DotASCIINode
    assert str(item.argument) == '""'


@pytest.mark.skip("Implement in Problem 7.##")
@typing.no_type_check
def test_dot_block() -> None:
    ret = parse("cat: .BLOCK 0x10")
    assert len(ret) == 1
    item: DotBlockNode = cast(DotBlockNode, ret[0])
    assert type(item) is DotBlockNode
    assert int(item.argument) == 0x10
    assert len(item) == 0x10
    assert item.symbol_decl and str(item.symbol_decl) == "cat"
    ret = parse(".BLOCK 10")
    item = cast(DotBlockNode, ret[0])
    assert type(item) is DotBlockNode
    assert int(item.argument) == 10
    assert len(item) == 10


@pytest.mark.skip("Implement in Problem 7.##")
@typing.no_type_check
def test_dot_byte() -> None:
    ret = parse("cat: .BYte 0x10")
    assert len(ret) == 1
    item: DotLiteralNode = cast(DotLiteralNode, ret[0])
    assert type(item) is DotLiteralNode
    assert int(item.argument) == 0x10
    assert len(item) == 1
    assert item.symbol_decl and str(item.symbol_decl) == "cat"
    ret = parse(".BYte 10")
    item = cast(DotLiteralNode, ret[0])
    assert type(item) is DotLiteralNode
    assert int(item.argument) == 10
    assert len(item) == 1


@pytest.mark.skip("Implement in Problem 7.##")
@typing.no_type_check
def test_dot_equate() -> None:
    ret = parse("cat: .EQUATE 0x10")
    assert len(ret) == 1
    item: DotEquateNode = cast(DotEquateNode, ret[0])
    assert type(item) is DotEquateNode
    assert int(item.argument) == 0x10
    assert len(item) == 0
    assert item.symbol_decl and str(item.symbol_decl) == "cat"
    assert int(item.symbol_decl) == 0x10

    ret = parse("cat: .EQUATE 10")
    assert len(ret) == 1
    item = cast(DotEquateNode, ret[0])
    assert type(item) is DotEquateNode
    assert int(item.argument) == 10
    assert len(item) == 0
    assert item.symbol_decl and str(item.symbol_decl) == "cat"
    assert int(item.symbol_decl) == 10

    # Strings
    ret = parse('cat: .EQUATE "a"\n')
    assert len(ret) == 1
    item = cast(DotEquateNode, ret[0])
    assert type(item) is DotEquateNode
    assert int(item.argument) == ord("a")
    assert len(item) == 0
    assert item.symbol_decl and str(item.symbol_decl) == "cat"
    assert int(item.symbol_decl) == ord("a")

    # Symbolic argument
    ret = parse("cat: .EQUATE cat")
    item = cast(DotEquateNode, ret[0])
    assert type(item) is ErrorNode


@pytest.mark.skip("Implement in Problem 7.##")
@typing.no_type_check
def test_dot_word() -> None:
    ret = parse("cat: .WORd 0x10")
    assert len(ret) == 1
    item: DotLiteralNode = cast(DotLiteralNode, ret[0])
    assert type(item) is DotLiteralNode
    assert int(item.argument) == 0x10
    assert len(item) == 2
    assert item.symbol_decl and str(item.symbol_decl) == "cat"
    ret = parse(".woRD 10")
    item = cast(DotLiteralNode, ret[0])
    assert type(item) is DotLiteralNode
    assert int(item.argument) == 10
    assert len(item) == 2
