import itertools
from typing import List, Tuple, cast, Sequence

from .arguments import Identifier, ArgumentType
from .ir import AddressableLine, listing, ErrorLine, IRLine
from .symbol import SymbolEntry


def calculate_addresses(
    parse_tree: Sequence[IRLine], base_address=0
) -> Tuple[List[IRLine], List[str]]:
    errors: List[str] = []
    ir: List[IRLine] = []
    address = base_address
    for node in parse_tree:
        if isinstance(node, ErrorLine):
            errors.append(node.source())
            continue
        elif isinstance(node, AddressableLine):
            ir.append(node)
        elif isinstance(node, IRLine):
            ir.append(node)
            continue
        else:
            continue

        line: AddressableLine = cast(AddressableLine, node)
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


def program_object_code(program: List[IRLine]) -> bytearray:
    oc = itertools.chain.from_iterable(
        (
            line.object_code()
            for line in program
            if isinstance(line, AddressableLine)
        )
    )
    return bytearray(oc)


def program_source(program: List[IRLine]) -> List[str]:
    return [line.source() for line in program]


def program_listing(program: List[IRLine]) -> List[str]:
    lst = itertools.chain.from_iterable(listing(line) for line in program)
    return list(lst)
