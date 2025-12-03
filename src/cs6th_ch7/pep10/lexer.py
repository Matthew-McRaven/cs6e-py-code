import io
import os
import string
from enum import Enum
from typing import Literal, List

import cs6th_ch7.pep10.tokens as tokens
from .tokens import Token
from ..utils.buffer import TokenProducer


class Lexer(TokenProducer[Token]):
    class States(Enum):
        START, COMMENT, IDENT, LEADING0, HEX_PRE = range(0, 5)
        HEX, SIGN, DEC, STOP = range(5, 9)

    def __init__(self, buffer: io.StringIO) -> None:
        self.buffer: io.StringIO = buffer

    def __iter__(self) -> "Lexer":
        return self

    def __next__(self) -> Token:
        state: Lexer.States = Lexer.States.START
        as_str_list: List[str] = []
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
                    elif ch == ",":
                        state = Lexer.States.STOP
                        token = tokens.Comma()
                    elif ch.isspace():
                        pass
                    elif ch == ";":
                        state = Lexer.States.COMMENT
                    elif ch.isalpha():
                        as_str_list.append(ch)
                        state = Lexer.States.IDENT
                    elif ch == "0":
                        state = Lexer.States.LEADING0
                    elif ch.isdecimal():
                        state = Lexer.States.DEC
                        as_int = ord(ch) - ord("0")
                    elif ch == "+" or ch == "-":
                        state = Lexer.States.SIGN
                        sign = -1 if ch == "-" else 1
                    else:
                        token = tokens.Invalid()

                case Lexer.States.COMMENT:
                    if ch == "\n":
                        self.buffer.seek(prev_pos, os.SEEK_SET)
                        state = Lexer.States.STOP
                        token = tokens.Comment("".join(as_str_list))
                    else:
                        as_str_list.append(ch)

                case Lexer.States.IDENT:
                    if ch.isalnum() or ch == "_":
                        as_str_list.append(ch)
                    elif ch == ":":
                        state = Lexer.States.STOP
                        token = tokens.Symbol("".join(as_str_list))
                    else:
                        self.buffer.seek(prev_pos, os.SEEK_SET)
                        state = Lexer.States.STOP
                        as_str = "".join(as_str_list)
                        token = tokens.Identifier(as_str)

                case Lexer.States.LEADING0:
                    if ch.isdigit():
                        as_int = ord(ch) - ord("0")
                        state = Lexer.States.DEC
                    elif ch == "x" or ch == "X":
                        state = Lexer.States.HEX_PRE
                    else:
                        self.buffer.seek(prev_pos, os.SEEK_SET)
                        state = Lexer.States.STOP
                        token = tokens.Decimal(0)

                case Lexer.States.HEX_PRE:
                    if ch in string.digits:
                        state = Lexer.States.HEX
                        as_int = as_int * 16 + (ord(ch) - ord("0"))
                    elif ch in string.hexdigits:
                        state = Lexer.States.HEX
                        digit = 10 + ord(ch.lower()) - ord("a")
                        as_int = as_int * 16 + digit
                    else:
                        token = tokens.Invalid()

                case Lexer.States.HEX:
                    if ch in string.digits:
                        as_int = as_int * 16 + (ord(ch) - ord("0"))
                    elif ch in string.hexdigits:
                        digit = 10 + ord(ch.lower()) - ord("a")
                        as_int = as_int * 16 + digit
                    else:
                        self.buffer.seek(prev_pos, os.SEEK_SET)
                        state = Lexer.States.STOP
                        token = tokens.Hex(as_int)

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

    def skip_to_next_line(self):
        while (ch := self.buffer.read(1)) != "\n" and len(ch) > 0:
            pass
