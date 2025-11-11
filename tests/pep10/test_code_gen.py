import pytest
from cs6th_ch7.pep10.code_gen import program_object_code, generate_code
from cs6th_ch7.pep10.ir import CommentLine, EmptyLine
from cs6th_ch7.pep10.parser import parse
from cs6th_ch7.pep10.symbol import SymbolTable


@pytest.mark.skip("Implement in Problem 7.##")  # FIGURE ONLY
def test_unary_object_code():
    parse_tree = parse("NOTA\nNOTA\nRET\n")
    ir, errors = generate_code(parse_tree)
    assert len(errors) == 0
    assert len(parse_tree) == 3 and len(ir) == 3
    assert program_object_code(ir) == bytearray([0x1E, 0x1E, 0x1])
    assert ir[0].address == 0 and ir[1].address == 1 and ir[2].address == 2


def test_nonunary_object_code():
    st = SymbolTable()
    parse_tree = parse(
        "cat:BR 3,i\ndog:ADDA 0x10,d\nCALL cat,i\n", symbol_table=st
    )
    ir, errors = generate_code(parse_tree)
    assert len(errors) == 0
    assert "cat" in st and int(st["cat"]) == 0
    assert "dog" in st and int(st["dog"]) == 3
    assert len(parse_tree) == 3 and len(ir) == 3
    assert program_object_code(ir) == bytearray(
        [0x24, 0x00, 0x03, 0x51, 0x00, 0x10, 0x36, 0x00, 0x00]
    )
    assert ir[0].address == 0 and ir[1].address == 3 and ir[2].address == 6


def test_comment_empty():
    parse_tree = parse("\n;test comment")
    ir, errors = generate_code(parse_tree)
    assert len(errors) == 0

    assert len(parse_tree) == 2 and len(ir) == 2
    assert program_object_code(ir) == bytearray()
    assert type(ir[0]) is EmptyLine and type(ir[1]) is CommentLine
