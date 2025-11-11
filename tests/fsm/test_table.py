from cs6th_ch7.fsm import Table


def test_table():
    fsm = Table()
    assert fsm.parse("h")
    assert fsm.parse("hi")
    assert fsm.parse("hi1")
    assert not fsm.parse("1hi")
    assert not fsm.parse("")
