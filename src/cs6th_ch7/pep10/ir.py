import itertools
from typing import List, Protocol, runtime_checkable
from dataclasses import dataclass

from .symbol import SymbolEntry
from .mnemonics import AddressingMode, INSTRUCTION_TYPES, as_int
from .arguments import ArgumentType


class IRLine(Protocol):
    def source(self) -> str: ...


@runtime_checkable
class ListableLine(IRLine, Protocol):
    def source(self) -> str: ...
    def object_code(self) -> bytearray: ...
    def __len__(self) -> int: ...


@runtime_checkable
class AddressableLine(ListableLine, Protocol):
    address: int | None


def source(
    op: str,
    args: List[str],
    symbol: SymbolEntry | None = None,
    comment: str | None = None,
) -> str:
    sym_str = f"{symbol}:" if symbol else ""
    comment_str = f";{comment}" if comment else ""
    return f"{sym_str:7}{op:7}{','.join(args):12}{comment_str}"


@dataclass
class ErrorLine:
    comment: str | None = None

    def source(self) -> str:
        message = self.comment or "Failed to parse line"
        return f";ERROR: {message}"

    def object_code(self) -> bytearray:
        return bytearray()

    def __len__(self):
        return 0

    def __repr__(self):
        return f"ErrorLine('{self.source()}')"


@dataclass
class EmptyLine:

    def source(self) -> str:
        return source("", [], None, None)

    def object_code(self) -> bytearray:
        return bytearray()

    def __len__(self):
        return 0

    def __repr__(self):
        return f"EmptyLine()"


@dataclass
class CommentLine:
    comment: str

    def source(self) -> str:
        return source("", [], None, self.comment)

    def object_code(self) -> bytearray:
        return bytearray()

    def __len__(self):
        return 0

    def __repr__(self):
        return f"CommentLine('{self.comment}')"


@dataclass
class DyadicLine:
    mnemonic: str
    argument: ArgumentType
    addressing_mode: AddressingMode
    symbol_decl: SymbolEntry | None = None
    comment: str | None = None
    address: int | None = None

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

    def __post_init__(self):
        if not self.mnemonic.isupper():
            self.mnemonic = self.mnemonic.upper()
        assert self.mnemonic in INSTRUCTION_TYPES

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


@dataclass
class MonadicLine:
    mnemonic: str
    symbol_decl: SymbolEntry | None = None
    comment: str | None = None
    address: int | None = None

    def source(self) -> str:
        mn = self.mnemonic.upper()
        return source(mn, [], self.symbol_decl, self.comment)

    def object_code(self) -> bytearray:
        bits = as_int(self.mnemonic)
        mn_bytes = bits.to_bytes(1, signed=False)
        return bytearray(mn_bytes)

    def __len__(self) -> int:
        return 1

    def __post_init__(self):
        if not self.mnemonic.isupper():
            self.mnemonic = self.mnemonic.upper()
        assert self.mnemonic in INSTRUCTION_TYPES

    def __repr__(self):
        symbol_text = f"{self.symbol_decl}:" if self.symbol_decl else ""
        components = [f"'{symbol_text}{self.mnemonic}'"]
        if self.comment:
            components.append(f"comment={self.comment}")
        if self.address:
            components.append(f"address={self.address}")
        return f"MonadicLine({','.join(components)})"


def listing(ir: ListableLine) -> List[str]:
    object_code = ir.object_code()
    oc_format = lambda oc: "".join(f"{i:02X}" for i in oc)
    if len(object_code) <= 3:
        line_object_code, object_code = object_code, bytearray(0)
    else:
        line_object_code = object_code[0:2]
        object_code = object_code[3:]
    if isinstance(ir, AddressableLine):
        address = f"{ir.address:04X}" if ir.address is not None else 4 * " "
    else:
        address = 4 * " "
    lines = [f"{address} {oc_format(line_object_code):6} {ir.source()}"]
    for b in itertools.batched(object_code, 3):
        lines.append(f"{'':4} {oc_format(b): 6}")
    return lines
