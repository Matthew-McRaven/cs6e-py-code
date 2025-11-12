import io
import os
import string
from enum import Enum
from typing import Literal, List

import cs6th_ch7.expr.tokens as tokens
from .tokens import Token
from cs6th_ch7.utils.buffer import TokenProducer


class Lexer(TokenProducer[Token]):
    class States(Enum):
        START, PAREN_OPEN, PAREN_CLOSE, PLUS, TIMES = range(0, 5)
        SIGN, DEC, STOP = range(5, 8)

    def __init__(self, buffer: io.StringIO) -> None:
        self.buffer: io.StringIO = buffer

    def __iter__(self) -> "Lexer":
        return self

    def __next__(self) -> Token:
        state: Lexer.States = Lexer.States.START
        as_int: int = 0
        sign: Literal[-1, 1] = 1
        token: Token = tokens.Empty()
        initial_pos = self.buffer.tell()

        while state != Lexer.States.STOP and (
            type(token) is not tokens.Invalid
        ):
            prev_pos = self.buffer.tell()
            ch: str = self.buffer.read(1)
            if len(ch) == 0:
                if initial_pos == prev_pos:
                    raise StopIteration()
                ch = "\n"
            match state:
                case Lexer.States.START:
                    if ch == "\n":
                        state = Lexer.States.STOP
                    elif ch == "(":
                        state = Lexer.States.STOP
                        token = tokens.ParenOpen()
                    elif ch == ")":
                        state = Lexer.States.STOP
                        token = tokens.ParenClose()
                    elif ch == "+":
                        state = Lexer.States.STOP
                        token = tokens.Plus()
                    elif ch == "*":
                        state = Lexer.States.STOP
                        token = tokens.Times()
                    elif ch.isspace():
                        pass
                    elif ch == "0":
                        state = Lexer.States.DEC
                    elif ch.isdecimal():
                        state = Lexer.States.DEC
                        as_int = int(ch)
                    elif ch == "+" or ch == "-":
                        state = Lexer.States.SIGN
                        sign = -1 if ch == "-" else 1
                    else:
                        token = tokens.Invalid()

                case Lexer.States.SIGN:
                    if ch in string.digits:
                        as_int = as_int * 10 + (ord(ch) - ord("0"))
                        state = Lexer.States.DEC
                    else:
                        token = tokens.Invalid()

                case Lexer.States.DEC:
                    if ch in string.digits:
                        as_int = as_int * 10 + (ord(ch) - ord("0"))
                    else:
                        self.buffer.seek(prev_pos, os.SEEK_SET)
                        state = Lexer.States.STOP
                        token = tokens.Decimal(sign * as_int)
                case _:
                    token = tokens.Invalid()

        return token
