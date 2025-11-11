from cs6th_ch7.fsm import Direct


def test_direct():
    fsm = Direct()
    assert fsm.parse("10") == (True, 10)
    assert fsm.parse("-10") == (True, -10)
    assert fsm.parse("-115") == (True, -115)
    assert not fsm.parse("--0")[0]
    assert not fsm.parse("++0")[0]
    assert not fsm.parse("+")[0]
