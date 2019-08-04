from opera.parser.yaml.node import Node


class TestInit:
    def test_constructor(self):
        node = Node("value", "name", 1, 2)

        assert node.value == "value"
        assert node.loc.stream_name == "name"
        assert node.loc.line == 1
        assert node.loc.column == 2


class TestDump:
    def test_null_dump(self):
        node = Node(None, "s", 1, 1)

        assert node.dump() == "NoneType(s:1:1)(None)"

    def test_bool_dump(self):
        node = Node(True, "s", 1, 1)

        assert node.dump() == "bool(s:1:1)(True)"

    def test_int_dump(self):
        node = Node(123, "s", 1, 1)

        assert node.dump() == "int(s:1:1)(123)"

    def test_sfloat_dump(self):
        node = Node(123.456, "s", 1, 1)

        assert node.dump() == "float(s:1:1)(123.456)"

    def test_str_dump(self):
        node = Node("string", "s", 1, 1)

        assert node.dump() == "str(s:1:1)(string)"

    def test_scalar_ignores_padding(self):
        node = Node("string", "s", 1, 1)

        assert node.dump("    ") == "str(s:1:1)(string)"

    def test_seq_dump(self):
        node = Node([Node(1, "s", 1, 1), Node("a", "k", 2, 3)], "u", 5, 6)

        assert node.dump() == (
            "list(u:5:6)[\n"
            "  int(s:1:1)(1),\n"
            "  str(k:2:3)(a)\n"
            "]"
        )

    def test_seq_dump_padded(self):
        node = Node([Node(1, "s", 1, 1), Node("a", "k", 2, 3)], "u", 5, 6)

        assert node.dump("   ") == (
            "list(u:5:6)[\n"
            "     int(s:1:1)(1),\n"
            "     str(k:2:3)(a)\n"
            "   ]"
        )

    def test_map_dump(self):
        node = Node({Node(1, "s", 1, 1): Node("a", "k", 2, 3)}, "u", 5, 6)

        assert node.dump() == (
            "dict(u:5:6){\n"
            "  int(s:1:1)(1): str(k:2:3)(a)\n"
            "}"
        )

    def test_map_dump_padded(self):
        node = Node({Node(1, "s", 1, 1): Node("a", "k", 2, 3)}, "u", 5, 6)

        assert node.dump("      ") == (
            "dict(u:5:6){\n"
            "        int(s:1:1)(1): str(k:2:3)(a)\n"
            "      }"
        )

    def test_dump_nested(self):
        child = Node([Node(1, "a", 1, 2), Node("a", "b", 3, 4)], "c", 5, 6)
        node = Node({Node(True, "d", 7, 8): child}, "e", 9, 0)

        assert node.dump() == (
            "dict(e:9:0){\n"
            "  bool(d:7:8)(True): list(c:5:6)[\n"
            "    int(a:1:2)(1),\n"
            "    str(b:3:4)(a)\n"
            "  ]\n"
            "}"
        )


class TestBare:
    def test_bare_scalar(self):
        assert Node(1, "a", 2, 3).bare == 1

    def test_bare_seq(self):
        node = Node([Node(1, "s", 1, 1), Node("a", "k", 2, 3)], "u", 5, 6)

        assert node.bare == [1, "a"]

    def test_bare_map(self):
        node = Node({Node(1, "s", 1, 1): Node("a", "k", 2, 3)}, "u", 5, 6)

        assert node.bare == {1: "a"}

    def test_base_nested(self):
        child = Node([Node(1, "s", 1, 1), Node("a", "k", 2, 3)], "u", 5, 6)
        node = Node({Node(1, "s", 1, 1): child}, "u", 5, 6)

        assert node.bare == {1: [1, "a"]}


class TestStr:
    def test_str(self):
        assert str(Node(0, "a", 1, 2)) == "int(a:1:2)(0)"
