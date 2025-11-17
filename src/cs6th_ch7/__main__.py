import argparse

from cs6th_ch7.expr.code_gen import expression_string, to_pep10_ir
from cs6th_ch7.expr.parser import ExpressionParser
from .fsm.lexer import Direct, Table, HexDirect
import io
from .pep10.lexer import Lexer
from .pep10.code_gen import (
    calculate_addresses,
    program_object_code,
    program_listing,
    program_source,
)
from .pep10.ir import ErrorLine
from .pep10.macro import MacroRegistry, add_OS_macros
from .pep10.parser import parse
from .pep10.symbol import SymbolTable, add_OS_symbols
import sys


def text_from_args(args):
    if "text" in args and args.text is not None:
        return args.text
    elif "file" in args and args.file is not None:
        with open(args.file, "r") as f:
            return "".join(f.readlines())
    else:
        raise RuntimeError("Expected either text or file")


def exec_fsm_table(args):
    text = text_from_args(args)
    p = Table()
    success = p.parse(text)
    print(f"{text} is{' ' if success else ' not '}a valid identifier")


def exec_fsm_direct(args):
    text = text_from_args(args)
    p = Direct()
    success, value = p.parse(text)
    if not success:
        print("Invalid Entry")
    else:
        print(f"Number = {value}")


def exec_fsm_hex(args):
    text = text_from_args(args)
    p = HexDirect()
    success, value = p.parse(text)
    if not success:
        print("Invalid Entry")
    else:
        print(f"Number = {value}")


def exec_lex(args):
    text = text_from_args(args)
    buffer = io.StringIO(text.rstrip() + "\n")
    lexer = Lexer(buffer)
    for token in lexer:
        print(repr(token))


def parse_wrapper(text: str):
    st, mr = SymbolTable(), MacroRegistry()
    add_OS_symbols(st), add_OS_macros(mr)
    ir = parse(text, symbol_table=st, macro_registry=mr)
    return ir


def generate_code_wrapper(parse_tree):
    parse_errors = list(filter(lambda n: type(n) is ErrorLine, parse_tree))
    if len(parse_errors) > 0:
        for error in parse_errors:
            print(error, file=sys.stderr)
        raise SyntaxError("Failed to parse program")
    ir, ir_errors = calculate_addresses(parse_tree)
    if len(ir_errors) > 0:
        for ir_error in ir_errors:
            print(ir_error, file=sys.stderr)
        raise SyntaxError("Failed to generate object code")
    return (
        program_object_code(ir),
        program_listing(ir),
        program_source(ir),
    )


def exec_expr(args):
    text = text_from_args(args)
    # Remove trailing whitespace while insuring input is \n terminated.
    buffer = io.StringIO(text.rstrip() + "\n")
    parser = ExpressionParser(buffer)
    expr_tokens = parser.E()
    print(expression_string(expr_tokens))


def exec_expr_codegen(args):
    text = text_from_args(args)
    # Remove trailing whitespace while insuring input is \n terminated.
    buffer = io.StringIO(text.rstrip() + "\n")
    parser = ExpressionParser(buffer)
    expr_tokens = parser.E()
    ir_lines = to_pep10_ir(expr_tokens)
    ir, ir_errors = calculate_addresses(ir_lines)
    if len(ir_errors) > 0:
        for ir_error in ir_errors:
            print(ir_error, file=sys.stderr)
        raise SyntaxError("Failed to generate object code")
    print("\n".join(x for x in program_listing(ir)))


def exec_parser(args):
    text = text_from_args(args)
    for line in parse_wrapper(text):
        print(repr(line))


def exec_codegen(args):
    text = text_from_args(args)
    ir = parse_wrapper(text)
    code, listing, source = generate_code_wrapper(ir)
    print("\n".join(listing))


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    parse_table = subparsers.add_parser(
        "table",
        help="A table-lookup FSM to recognize identifiers (Figure 7.28)",
    )

    parse_table.set_defaults(func=exec_fsm_table)
    parse_table_group = parse_table.add_mutually_exclusive_group(required=True)
    parse_table_group.add_argument("--text")
    parse_table_group.add_argument("--file")

    parse_fsm_direct = subparsers.add_parser(
        "direct",
        help="A direct-coded FSM to scan signed decimals (Figure 7.29)",
    )
    parse_fsm_direct.set_defaults(func=exec_fsm_direct)
    parse_direct_group = parse_fsm_direct.add_mutually_exclusive_group(
        required=True
    )
    parse_direct_group.add_argument("--text")
    parse_direct_group.add_argument("--file")

    parse_fsm_hex = subparsers.add_parser(
        "hexdirect",
        help="A direct-coded FSM to scan hex strings (Problem 7.18)",
    )
    parse_fsm_hex.set_defaults(func=exec_fsm_hex)
    parse_hex_group = parse_fsm_hex.add_mutually_exclusive_group(required=True)
    parse_hex_group.add_argument("--text")
    parse_hex_group.add_argument("--file")

    parse_lex = subparsers.add_parser(
        "lex", help="A multiple-token lexical analyzer for Pep/10 (Figure 7.34"
    )
    parse_lex.set_defaults(func=exec_lex)
    parse_lex_group = parse_lex.add_mutually_exclusive_group(required=True)
    parse_lex_group.add_argument("--text")
    parse_lex_group.add_argument("--file")

    parse_expr = subparsers.add_parser(
        "expr",
        help="A recursive descent parser for an expression grammar (Figure 7.41)",
    )
    parse_expr.set_defaults(func=exec_expr)
    parse_expr_group = parse_expr.add_mutually_exclusive_group(required=True)
    parse_expr_group.add_argument("--text")
    parse_expr_group.add_argument("--file")

    parse_parser = subparsers.add_parser(
        "parser", help="A recursive descent parser for Pep/10 (Figure 7.49)"
    )
    parse_parser.set_defaults(func=exec_parser)
    parse_parser_group = parse_parser.add_mutually_exclusive_group(
        required=True
    )
    parse_parser_group.add_argument("--text")
    parse_parser_group.add_argument("--file")

    parse_codegen = subparsers.add_parser(
        "codegen", help="A code generator for Pep/10 (Figure 7.xx)"
    )
    parse_codegen.set_defaults(func=exec_codegen)
    parse_codegen_group = parse_codegen.add_mutually_exclusive_group(
        required=True
    )
    parse_codegen_group.add_argument("--text")
    parse_codegen_group.add_argument("--file")

    parse_compile = subparsers.add_parser(
        "exprcode",
        help="A code generator for an expression grammar (Figure 7.xx)",
    )
    parse_compile.set_defaults(func=exec_expr_codegen)
    parse_compile = parse_compile.add_mutually_exclusive_group(required=True)
    parse_compile.add_argument("--text")
    parse_compile.add_argument("--file")

    # Print help by default if no subcommand is provided
    parser.set_defaults(func=lambda _: parser.print_help())

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    main()
