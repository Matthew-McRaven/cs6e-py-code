import enum
from typing import Dict


class Table:
    class States(enum.IntEnum):
        A = 0
        B = 1
        C = 2

    class Kind(enum.IntEnum):
        Letter = 0
        Digit = 1

    transitions: Dict[States, Dict[Kind, States]] = {
        States.A: {Kind.Letter: States.B, Kind.Digit: States.C},
        States.B: {Kind.Letter: States.B, Kind.Digit: States.B},
        States.C: {Kind.Letter: States.C, Kind.Digit: States.C},
    }

    def parse(self, text: str):
        state = Table.States.A
        for ch in text:
            kind = Table.Kind.Letter if ch.isalpha() else Table.Kind.Digit
            state = Table.transitions[state][kind]
        return state == Table.States.B


class Direct:
    class States(enum.Enum):
        I = 0
        F = 1
        M = 2
        STOP = 3

    def parse(self, text: str):
        text = text + "\n"
        state = Direct.States.I
        valid, magnitude, sign = True, 0, +1

        while state != Direct.States.STOP and valid:
            ch, text = text[0], text[1:] if len(text) > 1 else ""
            match state:
                case Direct.States.I:
                    if ch == "+":
                        sign, state = 1, Direct.States.F
                    elif ch == "-":
                        sign, state = -1, Direct.States.F
                    elif ch.isdigit():
                        magnitude, state = int(ch), Direct.States.M
                    else:
                        valid = False

                case Direct.States.F:
                    if ch.isdigit():
                        magnitude, state = int(ch), Direct.States.M
                    else:
                        valid = False

                case Direct.States.M:
                    if ch.isdigit():
                        magnitude = 10 * magnitude + int(ch)
                    elif ch == "\n":
                        state = Direct.States.STOP
                    else:
                        valid = False

        return valid, sign * magnitude if valid else None
