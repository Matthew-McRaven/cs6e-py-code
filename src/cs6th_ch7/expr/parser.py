import io
from typing import cast, List
import cs6th_ch7.expr.tokens as tokens
from .tokens import Token
from cs6th_ch7.utils.buffer import ParserBuffer
from .lexer import Lexer


class ExpressionParser:
    def __init__(self, buffer: io.StringIO):
        self.lexer = Lexer(buffer)
        self._buffer = ParserBuffer(self.lexer)

    def F(self) -> list[Token]:
        if self._buffer.may_match(tokens.ParenOpen):
            E = self.E()
            self._buffer.must_match(tokens.ParenClose)
            return [*E]
        elif token := self._buffer.must_match(tokens.Decimal):
            return [token]
        raise SyntaxError()

    def T(self) -> list[Token]:
        f = self.F()
        if times := self._buffer.may_match(tokens.Times):
            return [*f, *self.T(), times]
        return [*f]

    def E(self) -> list[Token]:
        t = self.T()
        if plus := self._buffer.may_match(tokens.Plus):
            return [*t, *self.E(), plus]
        return [*t]
