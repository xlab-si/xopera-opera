import math
import textwrap

import pytest

from opera.parser import yaml


def ystr(string):
    return textwrap.dedent(string.lstrip("\n").rstrip()) + "\n"


VALID_TEST_CASES = [
    ("sample", "sample"),
    ("123", 123),
    ("1.2", 1.2),
    ("NULL", None),
    (
        # language=yaml
        ystr("""
             test: map
             """),
        dict(test="map"),
    ),
    (
        # language=yaml
        ystr("""
             - list
             - 1
             - " is"
             - .Inf
             - here
             """),
        ["list", 1, " is", math.inf, "here"],
    ),
    (
        # language=yaml
        ystr("""
             d:
               - with
               - strs
               - dct: 1
                 of: 2
                 nums: 3
               - list
             """),
        {"d": ["with", "strs", {"dct": 1, "of": 2, "nums": 3}, "list"]},
    ),
    # FIXME(@tadeboro): This fails for some reasone. Need to dig through
    # pyyaml sources and find out why null constructor is not called in this
    # case.
    #  (
    #      ystr(""), None,
    #  )
]


class TestLoad:
    @pytest.mark.parametrize("input_string,output", VALID_TEST_CASES)
    def test_load_valid_yaml(self, input_string, output):
        assert yaml.load(input_string, "test").bare == output
