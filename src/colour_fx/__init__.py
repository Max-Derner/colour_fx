
from typing import Any, Tuple, Union


ansi_val: type[str] = str
ansi_code: type[str] = str
ansi_val_collection: type[list[list[ansi_val]]] = list[list[ansi_val]]
ansi_field: type[list[ansi_val_collection]] = list[ansi_val_collection]


class ANSIField:
    def __init__(self, template: Union[str, 'ANSIField']):
        self.raw_field: list[list[list[str]]] = self.__produce_raw_field(
            template
        )

    def __produce_raw_field(self, template: Union[str, 'ANSIField']):
        valid_template, err_reason = _is_valid_template(template)
        if valid_template:
            if isinstance(template, str):
                split_text = template.split('\n')
                no_lines = len(split_text)
                no_cols = max(
                    [len(line) for line in split_text]
                )
                return [
                    [[] for _ in range(no_cols)]
                    for _ in range(no_lines)
                ]
            if isinstance(template, type(self)):
                return [
                    [col.copy() for col in line]
                    for line in template.raw_field
                ]
        err_reason = err_reason or (
            "No reason given, please raise issue in GitHub repo."
        )
        err_msg = F"Template is not valid. Reason:\n{err_reason}"
        raise TypeError(err_msg)

    def copy(self):
        return ANSIField(self)

    def __eq__(self, other) -> bool:
        # Check right type
        if not isinstance(other, type(self)):
            return False
        this_raw = self.raw_field
        that_raw = other.raw_field
        # check raw_field type
        if not isinstance(that_raw, list):
            return False
        # check 1st dimensional length
        if len(this_raw) != len(that_raw):
            return False
        # check 2nd dimensional lengths
        for idx in range(len(this_raw)):
            if not isinstance(that_raw[idx], type(this_raw[idx])):
                return False
            if len(this_raw[idx]) != len(that_raw[idx]):
                return False
            # check 3rd dimensional similarity
            for i in range(len(this_raw[idx])):
                if this_raw[idx][i] != that_raw[idx][i]:
                    return False
        return True


def _is_valid_template(obj: Any) -> Tuple[bool, str]:
    """returns `(is_valid: bool, error_message: str)`

    error_message is empty is template is valid"""
    err_msg = ""
    if isinstance(obj, str):
        return True, ""
    else:
        err_msg += "Object is not string\n"
    is_ansi_field, field_err = _is_valid_ansi_field(obj)
    if is_ansi_field:
        return True, ""
    else:
        err_msg += field_err + "\n"
    return False, err_msg


def _is_valid_ansi_field(obj: Any) -> Tuple[bool, str]:
    """returns `(is_valid: bool, error_message: str)`

    Ansi fields must have three dimensions.

    The first dimension must contain lists that are all the same length,
    known as the nominal width.

    The second dimension must contain all lists of any length including
    zero.

    The third dimension must be all strings. These strings should be
    representing values for use in an ANSI escape sequence SGR, but we
    don't valid those values."""
    # check first dimensional list - the individual lines
    if not isinstance(obj, ANSIField):
        return False, "Object is not of class ANSIField"
    if len(obj.raw_field) < 1:
        return False, "raw_field is 1 dimensional"
    # check second dimensional list - the characters
    nominal_width = len(obj.raw_field[0])
    for line_no in range(len(obj.raw_field)):
        if not isinstance(obj.raw_field[line_no], list):
            return False, (
                F"No second dimension on raw_field at index [{line_no}]"
            )
        if (
            len(obj.raw_field[line_no]) < 1
            or len(obj.raw_field[line_no]) != nominal_width
        ):
            err_msg = (
                F"Incorrect width on raw_field at index [{line_no}]: expected "
                F"{nominal_width}, got {len(obj.raw_field[line_no])}"
            )
            return False, err_msg
        # check third dimensional list - the ANSI vals
        for col_no in range(len(obj.raw_field[line_no])):
            if not isinstance(obj.raw_field[line_no][col_no], list):
                err_msg = (
                    F"No third dimension on raw_field at index "
                    F"[{line_no}][{col_no}]"
                )
                return False, err_msg
            # check items in lowest depth list is made of strings
            for idx, value in enumerate(obj.raw_field[line_no][col_no]):
                if not isinstance(value, str):
                    err_msg = (
                        F"No string ANSI value found at index "
                        F"[{line_no}][{col_no}][{idx}]: "
                        F"{type(value)=}, {value=}"
                    )
                    return False, err_msg
    return True, ""


# Control Sequence Introducer
CSI = '\033['

# Select Graphic Rendition
SGR = 'm'


def compile_ansi_code(*ansi_vals: ansi_val) -> ansi_code:
    """Feed in any number of colour and style ANSI values and get a
    compiled ANSI code. Passing in no arguments yields the ANSI reset
    code which restores the default text colour and style.

    Example:

    ```python
    flashy_red = compile_ansi_code(
        Colour.RED,
        Colour.CYAN.background,
        Style.BLINK,
        Style.BOLD
    )
    reset = compile_ansi_code()
    print(F"Hello {flashy_red}WORLD{reset}!!!")
    ```"""
    ansi_vals = ansi_vals or ('0', )
    return CSI + ';'.join(ansi_vals) + SGR
