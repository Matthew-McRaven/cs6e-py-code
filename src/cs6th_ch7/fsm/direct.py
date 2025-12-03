import enum
from typing import Dict


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
