import pytest
from yaml.nodes import MappingNode, ScalarNode, SequenceNode

from opera.parser.yaml.resolver import Resolver


class TestResolve:
    @pytest.mark.parametrize("value", ["NULL", "Null", "null", "~", ""])
    def test_resolve_null(self, value):
        tag = Resolver().resolve(ScalarNode, value, (True, True))

        assert tag == "tag:yaml.org,2002:null"

    @pytest.mark.parametrize(
        "value", ["True", "true", "TRUE", "False", "false", "FALSE"],
    )
    def test_resolve_bool(self, value):
        tag = Resolver().resolve(ScalarNode, value, (True, True))

        assert tag == "tag:yaml.org,2002:bool"

    @pytest.mark.parametrize(
        "value", [
            "1", "0", "100", "987654", "-100", "+100", "00005", "054",
            "0o1", "0o0", "0o100", "0o765", "0o0000065",
            "0x1", "0x0", "0x100", "0x90abc", "0xAaBbFdE",
        ],
    )
    def test_resolve_int(self, value):
        tag = Resolver().resolve(ScalarNode, value, (True, True))

        assert tag == "tag:yaml.org,2002:int"

    @pytest.mark.parametrize(
        "value", [
            "+.inf", "-.inf", ".inf",
            "+.Inf", "-.Inf", ".Inf",
            "+.INF", "-.INF", ".INF",
            ".nan", ".NaN", ".NAN",
            "+.987", "-.765", ".0987", "+.6e-3", "-.5E+2", ".4E32",
            "+1.3", "-2.4", "3.5", "+1.3E-3", "-2.42e+5", "3.5e7",
            "+13E-3", "-2e+5", "3E7",
        ],
    )
    def test_resolve_float(self, value):
        tag = Resolver().resolve(ScalarNode, value, (True, True))

        assert tag == "tag:yaml.org,2002:float"

    @pytest.mark.parametrize(
        "value", [
            "abc", "1.2.3", "NaN", "INF", ".NAn", " ", "   ", "\n", "\t",
            "1 2", "https://url", ":bare", "multi\n  line",
        ],
    )
    def test_resolve_str(self, value):
        tag = Resolver().resolve(ScalarNode, value, (True, True))

        assert tag == "tag:yaml.org,2002:str"

    @pytest.mark.parametrize(
        "value", ["123", "1.3", ".nan", "+.Inf", "test"],
    )
    def test_resolve_seq(self, value):
        tag = Resolver().resolve(SequenceNode, value, (True, True))

        assert tag == "tag:yaml.org,2002:seq"

    @pytest.mark.parametrize(
        "value", ["123", "1.3", ".nan", "+.Inf", "test"],
    )
    def test_resolve_map(self, value):
        tag = Resolver().resolve(MappingNode, value, (True, True))

        assert tag == "tag:yaml.org,2002:map"
