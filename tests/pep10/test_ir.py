import pytest, typing
from cs6th_ch7.pep10.arguments import Decimal
from cs6th_ch7.pep10.ir import listing, DyadicLine
from cs6th_ch7.pep10.mnemonics import AddressingMode
from cs6th_ch7.pep10.symbol import SymbolTable


@pytest.mark.skip("Implement in Problem 7.##")
@typing.no_type_check
def test_unary():

    st = SymbolTable()
    s = st.define("cat")
    i = MonadicLine("RET", sym=s)
    i.address = 0
    assert i.source().rstrip() == "cat:   RET"
    assert "".join(listing(i)).rstrip() == "0000 01     cat:   RET"
    i = MonadicLine("RET")
    i.address = 0
    assert i.source().rstrip() == "       RET"
    assert "".join(listing(i)).rstrip() == "0000 01            RET"
    i = MonadicLine("RET", comment="hi")
    i.address = 0
    assert i.source().rstrip() == "       RET                ;hi"
    assert (
        "".join(listing(i)).rstrip()
        == "0000 01            RET                ;hi"
    )


def test_nonunary():
    st = SymbolTable()
    s = st.define("cat")
    i = DyadicLine("ADDA", Decimal(10), AddressingMode.SX, sym=s)
    i.address = 0
    assert i.source().rstrip() == "cat:   ADDA   10,sx"
    assert "".join(listing(i)).rstrip() == "0000 56000A cat:   ADDA   10,sx"
    i = DyadicLine("ADDA", Decimal(10), AddressingMode.SX)
    i.address = 0
    assert i.source().rstrip() == "       ADDA   10,sx"
    assert "".join(listing(i)).rstrip() == "0000 56000A        ADDA   10,sx"
    i = DyadicLine("ADDA", Decimal(10), AddressingMode.SX, comment="hi")
    i.address = 0
    assert i.source().rstrip() == "       ADDA   10,sx       ;hi"
    assert (
        "".join(listing(i)).rstrip()
        == "0000 56000A        ADDA   10,sx       ;hi"
    )
