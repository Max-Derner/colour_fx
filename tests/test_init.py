from colour_fx import compile_ansi_code, CSI, SGR


def test_compile_ansi_code():
    vals = ['0', '1', '2']

    code = compile_ansi_code(*vals)

    assert code == F"{CSI}0;1;2{SGR}"
