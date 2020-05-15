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
        assert str(Node(0, Location("a", 1, 2))) == "Node(a:1:2)[0]"
