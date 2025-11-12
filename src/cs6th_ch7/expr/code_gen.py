from typing import List
from .tokens import Token


def expression_string(expression: List[Token]) -> str:
    return " ".join(token.postfix_format() for token in expression)
