import math

import pytest
from yaml.error import Mark
from yaml.nodes import MappingNode, ScalarNode, SequenceNode

from opera.parser.yaml.constructor import Constructor


class TestNull:
    @pytest.mark.parametrize("value", ["NULL", "Null", "null", "~", ""])
    def test_construct_null(self, value):
        mark = Mark(None, None, 1, 2, None, None)
        node = ScalarNode(None, value, start_mark=mark)
        res = Constructor("null").construct_yaml_null(node)

        assert res.value is None
        assert res.loc.line == 2
        assert res.loc.column == 3
        assert res.loc.stream_name == "null"

    @pytest.mark.parametrize(
        "value,parse", [
            ("True", True), ("true", True), ("TRUE", True),
            ("False", False), ("false", False), ("FALSE", False),
        ],
    )
    def test_construct_bool_true(self, value, parse):
        mark = Mark(None, None, 4, 5, None, None)
        node = ScalarNode(None, value, start_mark=mark)
        res = Constructor("bool").construct_yaml_bool(node)

        assert res.value == parse
        assert res.loc.line == 5
        assert res.loc.column == 6
        assert res.loc.stream_name == "bool"

    @pytest.mark.parametrize(
        "value,parse", [
            ("1", 1), ("0", 0), ("100", 100), ("987654", 987654),
            ("-100", -100), ("+100", 100), ("00005", 5), ("054", 54),
            ("0o1", 1), ("0o0", 0), ("0o100", 64), ("0o765", 501),
            ("0o0000015", 13), ("0x1", 1), ("0x0", 0), ("0x100", 256),
            ("0x90abc", 592572), ("0xAaBbFdE", 179027934),
        ],
    )
    def test_construct_int(self, value, parse):
        mark = Mark(None, None, 3, 7, None, None)
        node = ScalarNode(None, value, start_mark=mark)
        res = Constructor("int").construct_yaml_int(node)

        assert res.value == parse
        assert res.loc.line == 4
        assert res.loc.column == 8
        assert res.loc.stream_name == "int"

    @pytest.mark.parametrize(
        "value,parse", [
            ("+.inf", math.inf), ("-.inf", -math.inf), (".inf", math.inf),
            ("+.Inf", math.inf), ("-.Inf", -math.inf), (".Inf", math.inf),
            ("+.INF", math.inf), ("-.INF", -math.inf), (".INF", math.inf),
            ("+.987", .987), ("-.765", -.765), (".0987", .0987),
            ("+.6e-3", .6e-3), ("-.5E+2", -.5e2), (".4E32", .4e32),
            ("+1.3", 1.3), ("-2.4", -2.4), ("3.5", 3.5), ("+1.3E-3", 1.3e-3),
            ("-2.42e+5", -2.42e5), ("3.5e7", 3.5e7), ("+13E-3", 13e-3),
            ("-2e+5", -2e5), ("3E7", 3e7),
        ],
    )
    def test_construct_float_no_nan(self, value, parse):
        mark = Mark(None, None, 2, 8, None, None)
        node = ScalarNode(None, value, start_mark=mark)
        res = Constructor("float").construct_yaml_float(node)

        assert res.value == parse
        assert res.loc.line == 3
        assert res.loc.column == 9
        assert res.loc.stream_name == "float"

    @pytest.mark.parametrize("value", [".nan", ".NaN", ".NAN"])
    def test_construct_float_nan_only(self, value):
        mark = Mark(None, None, 7, 1, None, None)
        node = ScalarNode(None, value, start_mark=mark)
        res = Constructor("float").construct_yaml_float(node)

        assert math.isnan(res.value)
        assert res.loc.line == 8
        assert res.loc.column == 2
        assert res.loc.stream_name == "float"

    @pytest.mark.parametrize(
        "value", [
            "abc", "1.2.3", "NaN", "INF", ".NAn", " ", "   ", "\n", "\t",
            "1 2", "https://url", ":bare", "multi\n  line",
        ],
    )
    def test_construct_str(self, value):
        mark = Mark(None, None, 0, 0, None, None)
        node = ScalarNode(None, value, start_mark=mark)
        res = Constructor("str").construct_yaml_str(node)

        assert res.value == value
        assert res.loc.line == 1
        assert res.loc.column == 1
        assert res.loc.stream_name == "str"

    def test_construct_seq(self):
        mark = Mark(None, None, 4, 3, None, None)
        children = [
            ScalarNode("tag:yaml.org,2002:int", str(i), start_mark=mark)
            for i in range(4)
        ]
        node = SequenceNode(None, children, start_mark=mark)
        # Sequences are single-element generators (lazy parsing) that we need
        # to exhaust. Simplest way of doing this is to assign to a single
        # element tuple and let the python do all the iterator funky-ness.
        res, = Constructor("seq").construct_yaml_seq(node)

        assert [0, 1, 2, 3] == [child.value for child in res.value]
        assert res.loc.line == 5
        assert res.loc.column == 4
        assert res.loc.stream_name == "seq"

    def test_construct_map(self):
        mark = Mark(None, None, 8, 8, None, None)
        children = [
            (
                ScalarNode("tag:yaml.org,2002:str", str(i), start_mark=mark),
                ScalarNode("tag:yaml.org,2002:int", str(i), start_mark=mark),
            )
            for i in range(2)
        ]
        node = MappingNode(None, children, start_mark=mark)
        res, = Constructor("map").construct_yaml_map(node)

        assert {"0": 0, "1": 1} == {
            k.value: v.value for k, v in res.value.items()
        }
        assert res.loc.line == 9
        assert res.loc.column == 9
        assert res.loc.stream_name == "map"
