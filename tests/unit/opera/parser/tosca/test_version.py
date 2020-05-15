import pytest

from opera.error import ParseError
from opera.parser.tosca.version import Version
from opera.parser.yaml.node import Node


class TestValidate:
  @pytest.mark.parametrize("version", [
      "0.0", "0.1", "1.1", "123.456", "1.2.0", "1.2.32", "1.2.3.test",
      "3.4.5.0rev_a", "6.7.8.a-0", "1.3.6.b-123", "1.2.3.4-5",
  ])
  def test_valid_version(self, version):
      Version.validate(Node(version))

  @pytest.mark.parametrize("version", [
      "", " ", "garbage", "1", "01.0", "1.02", "1.2.03", "1.2-5", "1-2",
      "1.2.in-va-lid", "1.2.3-bad", "1.2.3.4-bad",
  ])
  def test_invalid_version(self, version):
      with pytest.raises(ParseError, match="version"):
          Version.validate(Node(version))
