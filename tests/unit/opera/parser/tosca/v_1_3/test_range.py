import math

import pytest

from opera.error import ParseError
from opera.parser.tosca.v_1_3.range import Range
from opera.parser.yaml.node import Node


class TestValidate:
    @pytest.mark.parametrize("data", [
        "[1, 2]", "[3, UNBOUNDED]", "- 3\n- 6",
    ])
    def test_with_valid_data(self, data, yaml_ast):
        Range.validate(yaml_ast(data))

    @pytest.mark.parametrize("data", [
        "abc", "4," "{}", "3.4", "false", "null",         # Invalid types
        "[]", "[1]", "[1, 2, 3]", "[1, 2, 3, 4]",         # Invalid cardinality
        "[a, 1]", "[2.3, 1]", "[false, 1]", "[null, 1]",  # Invalid lo type
        "[0, 1.3]", "[0, true]", "[0, null]", "[0, {}]",  # Invalid hi type
        "[0, a]", "[0, \"\"]", "[0, BAD]",                # Invalid hi string
        "[5, 2]", "[-3, -6]", "[4, -3]",                  # lo > hi
    ])
    def test_invalid_data(self, data, yaml_ast):
        with pytest.raises(ParseError):
            Range.validate(yaml_ast(data))


class TestBuild:
    @pytest.mark.parametrize("input,output", [
        ("[1, 2]", (1, 2)), ("[-4, 5]", (-4, 5)),
        ("[0, UNBOUNDED]", (0, math.inf)),
    ])
    def test_construction(self, input, output, yaml_ast):
        assert Range.build(yaml_ast(input)).data == output
