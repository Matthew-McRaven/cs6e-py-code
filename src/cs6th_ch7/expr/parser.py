import io
from typing import cast, List
import cs6th_ch7.expr.tokens as tokens
from .tokens import Token
from cs6th_ch7.utils.buffer import ParserBuffer
from .lexer import Lexer


class ExpressionParser:
    def __init__(self, buffer: io.StringIO):
        self._lexer = Lexer(buffer)
        self._buffer = ParserBuffer(self._lexer)

    # 3. <F> -> ( <E> )
    # 4. <F> -> DECIMAL
    def F(self) -> list[Token]:
        if self._buffer.may_match(tokens.ParenOpen):
            e = self.E()
            self._buffer.must_match(tokens.ParenClose)
            return e
        return [self._buffer.must_match(tokens.Decimal)]

    # 2. <T> -> <F> [* <T>]
    def T(self) -> list[Token]:
        f = self.F()
        if times := self._buffer.may_match(tokens.Times):
            t = self.T()
            return [*f, *t, times]
        return f

    # 1. <E> -> <T> [+ <E>]
    def E(self) -> list[Token]:
        t = self.T()
        if plus := self._buffer.may_match(tokens.Plus):
            e = self.E()
            return [*t, *e, plus]
        return t
