import itertools
from typing import List, Tuple, cast

from .arguments import Identifier
from .ir import Listable, listing, ErrorLine

from .symbol import SymbolEntry
from .types import ParseTreeNode, ArgumentType


def generate_code(
    parse_tree: List[ParseTreeNode], base_address=0
) -> Tuple[List[Listable], List[str]]:
    errors: List[str] = []
    ir: List[Listable] = []
    address = base_address
    for node in parse_tree:
        if isinstance(node, ErrorLine):
            errors.append(node.source())
            continue
        elif isinstance(node, Listable):
            ir.append(node)
        else:
            continue

        line: Listable = cast(Listable, node)
        line.address = address
        # Check for multiply defined symbols, and assign addresses to symbol declarations
        if maybe_symbol := getattr(node, "symbol_decl", None):
            symbol: SymbolEntry = maybe_symbol
            if symbol.is_multiply_defined():
                errors.append(f"Multiply defined symbol: {symbol}")
            else:
                symbol.value = address

        # Check that symbols used as arguments are not undefined.
        if maybe_argument := getattr(line, "argument", None):
            argument: ArgumentType = maybe_argument
            if type(argument) is Identifier and argument.symbol.is_undefined():
                errors.append(f"Undefined symbol: {argument.symbol}")
        address += len(line)

    return ir, errors


def program_object_code(program: List[Listable]) -> bytearray:
    oc = itertools.chain.from_iterable((line.object_code() for line in program))
    return bytearray(oc)


def program_source(program: List[Listable]) -> List[str]:
    return [line.source() for line in program]


def program_listing(program: List[Listable]) -> List[str]:
    lst = itertools.chain.from_iterable(listing(line) for line in program)
    return list(lst)
