import pytest

from opera.parser.tosca.type import Type


class TestIsValidInternalType:
    @pytest.mark.parametrize("typ", [
        "a", "", "123", "int", "str", "bla", "STRING", "FLOAT", "NULL", "Map",
        "liST", "Bool", "bool", "BOOL", "Timestamp", "ranGE",
    ])
    def test_invalid_types(self, typ):
        assert Type.is_valid_internal_type(typ) is False

    @pytest.mark.parametrize("typ", [
        "string", "integer", "float", "boolean", "null",
        "timestamp", "version", "range", "list", "map", "scalar-unit.size",
        "scalar-unit.time", "scalar-unit.frequency", "scalar-unit.bitrate",
    ])
    def test_valid_built_in_types(self, typ):
        assert Type.is_valid_internal_type(typ) is True
