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
