from opera.parser.utils.location import Location
from opera.parser.yaml.node import Node


class TestInit:
    def test_constructor(self):
        node = Node("value", Location("name", 1, 2))

        assert node.value == "value"
        assert node.loc.stream_name == "name"
        assert node.loc.line == 1
        assert node.loc.column == 2

    def test_empty_loc_constructor(self):
        node = Node("value")

        assert node.value == "value"
        assert node.loc.stream_name == ""
        assert node.loc.line == 0
        assert node.loc.column == 0


class TestDump:
    def test_null_dump(self):
        node = Node(None, Location("s", 1, 1))

        assert node.dump() == "NoneType(s:1:1)(None)"

    def test_bool_dump(self):
        node = Node(True, Location("s", 1, 1))

        assert node.dump() == "bool(s:1:1)(True)"

    def test_int_dump(self):
        node = Node(123, Location("s", 1, 1))

        assert node.dump() == "int(s:1:1)(123)"

    def test_sfloat_dump(self):
        node = Node(123.456, Location("s", 1, 1))

        assert node.dump() == "float(s:1:1)(123.456)"

    def test_str_dump(self):
        node = Node("string", Location("s", 1, 1))

        assert node.dump() == "str(s:1:1)(string)"

    def test_scalar_ignores_padding(self):
        node = Node("string", Location("s", 1, 1))

        assert node.dump("    ") == "str(s:1:1)(string)"

    def test_seq_dump(self):
        node = Node([Node(1), Node("a")])

        assert node.dump() == (
            "list(:0:0)[\n"
            "  int(:0:0)(1),\n"
            "  str(:0:0)(a)\n"
            "]"
        )

    def test_seq_dump_padded(self):
        node = Node([
            Node(1, Location("s", 1, 1)),
            Node("a", Location("k", 2, 3)),
        ], Location("u", 5, 6))

        assert node.dump("   ") == (
            "list(u:5:6)[\n"
            "     int(s:1:1)(1),\n"
            "     str(k:2:3)(a)\n"
            "   ]"
        )

    def test_map_dump(self):
        node = Node({Node(1): Node("a")})

        assert node.dump() == (
            "dict(:0:0){\n"
            "  int(:0:0)(1): str(:0:0)(a)\n"
            "}"
        )

    def test_map_dump_padded(self):
        node = Node({Node(1): Node("a")})

        assert node.dump("      ") == (
            "dict(:0:0){\n"
            "        int(:0:0)(1): str(:0:0)(a)\n"
            "      }"
        )

    def test_dump_nested(self):
        node = Node({
            Node(True): Node([Node(1), Node("a")])
        })

        assert node.dump() == (
            "dict(:0:0){\n"
            "  bool(:0:0)(True): list(:0:0)[\n"
            "    int(:0:0)(1),\n"
            "    str(:0:0)(a)\n"
            "  ]\n"
            "}"
        )


class TestBare:
    def test_bare_scalar(self):
        assert Node(1).bare == 1

    def test_bare_seq(self):
        assert Node([Node(1), Node("a")]).bare == [1, "a"]

    def test_bare_map(self):
        assert Node({Node(1): Node("a")}).bare == {1: "a"}

    def test_base_nested(self):
        node = Node({
            Node(1): Node([Node(1), Node("a")]),
        })

        assert node.bare == {1: [1, "a"]}


class TestStr:
    def test_str(self):
        assert str(Node(0, Location("a", 1, 2))) == "int(a:1:2)(0)"
