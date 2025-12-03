from io import StringIO

import pytest

from cs6th_ch7.pep10.lexer import Lexer
import cs6th_ch7.pep10.tokens as tokens


def test_lexer_empty():
    tk = Lexer(StringIO("   \n  "))
    assert type(tok := next(tk)) is tokens.Empty
    assert type(tok := next(tk)) is tokens.Empty


def test_lexer_comma():
    tk = Lexer(StringIO("   ,\n,  "))
    assert type(tok := next(tk)) is tokens.Comma
    assert type(tok := next(tk)) is tokens.Empty
    assert type(tok := next(tk)) is tokens.Comma
    assert type(tok := next(tk)) is tokens.Empty


def test_lexer_comment():
    tk = Lexer(StringIO(" ;Comment here\n"))
    assert type(tok := next(tk)) is tokens.Comment
    assert tok.value == "Comment here"
    assert type(tok := next(tk)) is tokens.Empty


def test_lexer_identifier():
    tk = Lexer(StringIO("a bCd b0 b9 a_word "))
    assert type(tok := next(tk)) == tokens.Identifier
    assert tok.value == "a"
    assert type(tok := next(tk)) == tokens.Identifier
    assert tok.value == "bCd"
    assert type(tok := next(tk)) == tokens.Identifier
    assert tok.value == "b0"
    assert type(tok := next(tk)) == tokens.Identifier
    assert tok.value == "b9"
    assert type(tok := next(tk)) == tokens.Identifier
    assert tok.value == "a_word"


def test_lexer_symbol():
    tk = Lexer(StringIO("a: bCd: b0: b9: a_word: "))
    assert type(tok := next(tk)) is tokens.Symbol
    assert tok.value == "a"
    assert type(tok := next(tk)) is tokens.Symbol
    assert tok.value == "bCd"
    assert type(tok := next(tk)) is tokens.Symbol
    assert tok.value == "b0"
    assert type(tok := next(tk)) is tokens.Symbol
    assert tok.value == "b9"
    assert type(tok := next(tk)) is tokens.Symbol
    assert tok.value == "a_word"


def test_lexer_unsigned_decimal():
    tk = Lexer(StringIO("0 00 000 10 65537 "))
    assert type(tok := next(tk)) is tokens.Decimal
    assert tok.value == 0
    assert type(tok := next(tk)) is tokens.Decimal
    assert tok.value == 0
    assert type(tok := next(tk)) is tokens.Decimal
    assert tok.value == 0
    assert type(tok := next(tk)) is tokens.Decimal
    assert tok.value == 10
    assert type(tok := next(tk)) is tokens.Decimal
    assert tok.value == 65537


def test_lexer_positive_decimal():
    tk = Lexer(StringIO("+0 +00 +000 +10 +65537 "))
    assert type(tok := next(tk)) is tokens.Decimal
    assert tok.value == 0
    assert type(tok := next(tk)) is tokens.Decimal
    assert tok.value == 0
    assert type(tok := next(tk)) is tokens.Decimal
    assert tok.value == 0
    assert type(tok := next(tk)) is tokens.Decimal
    assert tok.value == 10
    assert type(tok := next(tk)) is tokens.Decimal
    assert tok.value == 65537


def test_lexer_negative_decimal():
    tk = Lexer(StringIO("-0 -00 -000 -10 -65537 "))
    assert type(tok := next(tk)) is tokens.Decimal
    assert tok.value == 0
    assert type(tok := next(tk)) is tokens.Decimal
    assert tok.value == 0
    assert type(tok := next(tk)) is tokens.Decimal
    assert tok.value == 0
    assert type(tok := next(tk)) is tokens.Decimal
    assert tok.value == -10
    assert type(tok := next(tk)) is tokens.Decimal
    assert tok.value == -65537


def test_lexer_sign_needs_digit():
    tk = Lexer(StringIO("- "))
    assert type(next(tk)) is tokens.Invalid


def test_lexer_hexadecimal():
    tk = Lexer(StringIO("0x0 0X000  0x1 0x10 0x10000 "))
    assert type(tok := next(tk)) is tokens.Hexadecimal
    assert tok.value == 0x0
    assert type(tok := next(tk)) is tokens.Hexadecimal
    assert tok.value == 0
    assert type(tok := next(tk)) is tokens.Hexadecimal
    assert tok.value == 1
    assert type(tok := next(tk)) is tokens.Hexadecimal
    assert tok.value == 0x10
    assert type(tok := next(tk)) is tokens.Hexadecimal
    assert tok.value == 0x1_00_00


def test_lexer_hex_needs_digit():
    tk = Lexer(StringIO("0x "))
    assert type(next(tk)) is tokens.Invalid


@pytest.mark.skip("Implement in Problem 7.##")  # FIGURE ONLY
def test_lexer_dot():
    tk = Lexer(StringIO(".a .bCd .b0 .b9 .a_word "))
    assert type(tok := next(tk)) is tokens.Dot
    assert tok.value == "a"
    assert type(tok := next(tk)) is tokens.Dot
    assert tok.value == "bCd"
    assert type(tok := next(tk)) is tokens.Dot
    assert tok.value == "b0"
    assert type(tok := next(tk)) is tokens.Dot
    assert tok.value == "b9"
    assert type(tok := next(tk)) is tokens.Dot
    assert tok.value == "a_word"


@pytest.mark.skip("Implement in Problem 7.##")  # FIGURE ONLY
def test_lexer_dot_requires_char():
    tk = Lexer(StringIO(". "))
    assert type(tok := next(tk)) is tokens.Invalid

    tk = Lexer(StringIO(".0 "))
    assert type(tok := next(tk)) is tokens.Invalid


@pytest.mark.skip("Implement in Problem 7.##")  # FIGURE ONLY
def test_lexer_unescaped_string():
    tk = Lexer(StringIO('"Hello world"'))
    assert type(tok := next(tk)) is tokens.String
    assert tok.value == b"Hello world"
    tk = Lexer(StringIO('""'))
    assert type(tok := next(tk)) is tokens.String
    assert tok.value == b""
    tk = Lexer(StringIO('" "'))
    assert type(tok := next(tk)) is tokens.String
    assert tok.value == b" "
    tk = Lexer(StringIO('"\'"'))
    assert type(tok := next(tk)) is tokens.String
    assert tok.value == b"'"


# TODO: test that characters are correctly rejected during lexing
# TODO: test that strings with escape characters do not crash
