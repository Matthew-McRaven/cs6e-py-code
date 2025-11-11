import itertools
from typing import List, TypeAlias, Literal

from .arguments import StringConstant
from .mnemonics import (
    AddressingMode,
    INSTRUCTION_TYPES,
    BITS,
    as_int,
)
from .symbol import SymbolEntry
from .types import ArgumentType, Listable, ParseTreeNode


def source(
    op: str,
    args: List[str],
    symbol: SymbolEntry | None = None,
    comment: str | None = None,
) -> str:
    sym_str = f"{symbol}:" if symbol else ""
    comment_str = f";{comment}" if comment else ""
    return f"{sym_str:7}{op:7}{','.join(args):12}{comment_str}"


class ErrorLine:
    def __init__(self, error: str | None = None) -> None:
        self.comment: str | None = error
        self.address: int | None = None

    def source(self) -> str:
        message = self.comment or "Failed to parse line"
        return f";ERROR: {message}"

    def object_code(self) -> bytearray:
        return bytearray()

    def __len__(self):
        return 0

    def __repr__(self):
        return f"ErrorLine('{self.source()}')"


class EmptyLine:
    def __init__(self) -> None:
        self.comment: str | None = None
        self.address: int | None = None

    def source(self) -> str:
        return source("", [], None, None)

    def object_code(self) -> bytearray:
        return bytearray()

    def __len__(self):
        return 0

    def __repr__(self):
        return f"EmptyLine()"


class CommentLine:
    def __init__(self, comment: str):
        self.comment: str | None = comment
        self.address: int | None = None

    def source(self) -> str:
        return source("", [], None, self.comment)

    def object_code(self) -> bytearray:
        return bytearray()

    def __len__(self):
        return 0

    def __repr__(self):
        return f"CommentLine('{self.comment}')"


class DyadicLine:
    def __init__(
        self,
        mn: str,
        argument: ArgumentType,
        am: AddressingMode,
        sym: SymbolEntry | None = None,
        comment: str | None = None,
    ):
        self.symbol_decl: SymbolEntry | None = sym
        mn = mn.upper()
        assert mn in INSTRUCTION_TYPES
        self.mnemonic = mn
        self.addressing_mode: AddressingMode = am
        self.argument: ArgumentType = argument
        self.comment: str | None = comment
        self.address: int | None = None

    def source(self) -> str:
        args = [str(self.argument), self.addressing_mode.name.lower()]
        mn = self.mnemonic.upper()
        return source(mn, args, self.symbol_decl, self.comment)

    def object_code(self) -> bytearray:
        bits = as_int(self.mnemonic, am=self.addressing_mode)
        mn_bytes = bits.to_bytes(1, signed=False)
        arg_bytes = int(self.argument).to_bytes(2)
        return bytearray(mn_bytes + arg_bytes)

    def __len__(self) -> int:
        return 3

    def __repr__(self):
        symbol_text = f"{self.symbol_decl}:" if self.symbol_decl else ""
        components = [
            f"'{symbol_text}{self.mnemonic} {str(self.argument)},{self.addressing_mode.name.lower()}'"
        ]
        if self.comment:
            components.append(f"comment={self.comment}")
        if self.address:
            components.append(f"address={self.address}")
        return f"DyadicLine({','.join(components)})"


def listing(ir: Listable) -> List[str]:
    object_code = ir.object_code()
    oc_format = lambda oc: "".join(f"{i:02X}" for i in oc)
    if len(object_code) <= 3:
        line_object_code, object_code = object_code, bytearray(0)
    else:
        line_object_code = object_code[0:2]
        object_code = object_code[3:]

    address = f"{ir.address:04X}" if ir.address is not None else 4 * " "
    lines = [f"{address} {oc_format(line_object_code):6} {ir.source()}"]
    for b in itertools.batched(object_code, 3):
        lines.append(f"{'':4} {oc_format(b): 6}")
    return lines
