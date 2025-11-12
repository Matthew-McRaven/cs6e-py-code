from dataclasses import dataclass


@dataclass
class Empty:
    def postfix_format(self) -> str:
        return ""


@dataclass
class Invalid:
    def postfix_format(self) -> str:
        return ""


@dataclass
class Plus:
    def postfix_format(self) -> str:
        return "+"


@dataclass
class Times:
    def postfix_format(self) -> str:
        return "*"


@dataclass
class ParenOpen:
    def postfix_format(self) -> str:
        return ""


@dataclass
class ParenClose:
    def postfix_format(self) -> str:
        return ""


@dataclass
class Decimal:
    value: int

    def postfix_format(self) -> str:
        return f"{self.value}"


type Token = Empty | Invalid | Decimal | Plus | Times | ParenOpen | ParenClose
