from pytest import mark, raises

from colour_fx import (
    compile_ansi_code,
    CSI,
    SGR,
    ANSIField,
    _is_valid_template
)


def test_compile_ansi_code():
    vals = ['0', '1', '2']

    code = compile_ansi_code(*vals)

    assert code == F"{CSI}0;1;2{SGR}"


def test_compile_ansi_code_defaults_to_reset_code():

    code = compile_ansi_code()

    assert code == F"{CSI}0{SGR}"


class TestANSIField:
    poor_raw_fields = [
        # incorrect types
        1,
        1.0,
        {},
        set(),
        False,
        # correct type, incorrect form
        [],  # only 1 dimension
        [[]],  # only 2 dimensions
        [[], [], []],  # still only 2 dimensions
        [  # 3 dimensions, but fails on width
            [[], [], []],
            [[], []],
            [[], [], []],
        ],
        [  # 2.5 dimensions
            [[], [], []],
            ['should', 'be', 'lists'],
            [[], [], []],
        ],
        [  # 2.5 dimensions
            [[], [], []],
            'should be 2D list',
            [[], [], []],
        ],
        [  # 3 dimensions, but fails on incorrect type
            [[], [], []],
            [[], [1], []],
            [[], [], []],
        ],
    ]
    poor_ansi_fields = [ANSIField('.') for _ in range(len(poor_raw_fields))]
    for idx, raw_field in enumerate(poor_raw_fields):
        poor_ansi_fields[idx].raw_field = raw_field

    blank_ansi = ANSIField('')
    blank_ansi.raw_field = [
        [[] for _ in range(10)]
        for _ in range(5)
    ]
    filled_ansi = ANSIField('')
    filled_ansi.raw_field = [
        [['a', 'p', 'e'], ['b', 'e', 'd'], ['c', 'a', 't']],
        [['h'], ['i'], []],
        [['h', 'a', 'p', 'p', 'y'], [], ['p', 'a', 't', 'h']]
    ]
    feed_pairs = [
        (
            ' \n\n          \n\n ',
            blank_ansi
        ),
        (

            blank_ansi,
            blank_ansi
        ),
        (
            filled_ansi,
            filled_ansi
        )
    ]

    @mark.parametrize('template', poor_raw_fields)
    def test_is_valid_template_error_detection(self, template):
        valid, err_msg = _is_valid_template(template)

        assert not valid, F"Assumed valid: {template=}"
        assert err_msg != "", "No helpful error message"

    @mark.parametrize('template', poor_ansi_fields)
    def test_produce_ansi_field_sad_path(self, template):
        with raises(TypeError):
            ANSIField(template)

    @mark.parametrize('feed1, feed2', feed_pairs)
    def test_equality(self, feed1, feed2):
        ansi_field_1 = ANSIField(feed1)
        ansi_field_2 = ANSIField(feed2)

        assert ansi_field_1 == ansi_field_2

    @mark.parametrize('ansi_field', poor_ansi_fields)
    def test_equality_for_bad_raw_fields(self, ansi_field):
        input_text = (
            "abc\n"
            "123\n"
            "xyz"
        )
        ansi_field_1 = ANSIField(input_text)

        assert ansi_field_1 != ansi_field
    

    @mark.parametrize('random_obj', [
        1,
        1.0,
        'hi',
        True,
        None,
        ...,
        [],
        [[]],
        [[['36']]],
        {},
        set(),
        (1, 'noooooo'),
    ])
    def test_equality_with_random_types(self, random_obj):
        input_text = (
            "Hello,\n"
            "Hi\n"
            "Hey"
        )
        ansi_field = ANSIField(input_text)

        assert ansi_field != random_obj


