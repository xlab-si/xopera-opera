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
        ystr("""
             test: map
             """),
        dict(test="map"),
    ),
    (
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
    # FIXME(@tadeboro): This fails for some reason. Need to dig through
    # pyyaml sources and find out why null constructor is not called in this
    # case.
    #  (
    #      ystr(""), None,
    #  )
]


class TestLoad:
    @pytest.mark.parametrize("input_yaml,output_object", VALID_TEST_CASES)
    def test_load_valid_yaml(self, input_yaml, output_object):
        assert yaml.load(input_yaml, "test").bare == output_object
