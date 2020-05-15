import pytest

from opera.error import ParseError
from opera.parser.tosca.v_1_3.status import Status
from opera.parser.yaml.node import Node


class TestValidate:
    @pytest.mark.parametrize(
        "status", ["supported", "unsupported", "experimental", "deprecated"],
    )
    def test_valid_status(self, status):
        Status.validate(Node(status))

    @pytest.mark.parametrize(
        "status", ["some", "random", "stuff", 1, 2, [], {}, (), 1.2, False],
    )
    def test_invalid_status(self, status):
        with pytest.raises(ParseError):
            Status.validate(Node(status))
