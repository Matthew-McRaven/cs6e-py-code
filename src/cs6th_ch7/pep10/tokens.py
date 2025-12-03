from dataclasses import dataclass


@dataclass
class Identifier:
    value: str


@dataclass
class Symbol:
    value: str


@dataclass
class Comment:
    value: str


@dataclass
class Empty: ...


@dataclass
class Invalid: ...


@dataclass
class Comma: ...


@dataclass
class Decimal:
    value: int


@dataclass
class Hexadecimal:
    value: int


@dataclass
class Dot:
    value: str


@dataclass
class String:
    value: bytearray


@dataclass
class Macro:
    value: str


type Token = Empty | Invalid | Comma | Decimal | Hexadecimal | Comment | Identifier | Symbol | Dot | String | Macro
