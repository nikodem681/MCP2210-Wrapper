import re
from enum import IntEnum

from conftest import HEADER
from instrumentation.PCBs import constants


def header_defines():
    with open(HEADER, encoding="latin-1") as f:
        text = f.read()
    return {name: int(value, 0) for name, value in re.findall(r"#define\s+(MCP2210_\w+)\s+(0x[0-9A-Fa-f]+|\d+)", text)}


def test_enum_values_match_the_header():
    defines = header_defines()
    checked = 0
    for enum in vars(constants).values():
        if isinstance(enum, type) and issubclass(enum, IntEnum) and enum is not IntEnum:
            for name, member in enum.__members__.items():
                if name in defines:
                    assert member == defines[name], f"{enum.__name__}.{name}"
                    checked += 1
    assert checked >= 14


def test_output_alias():
    assert constants.dfltGpioDir.MCP2210_OUPTUT is constants.dfltGpioDir.MCP2210_OUTPUT
