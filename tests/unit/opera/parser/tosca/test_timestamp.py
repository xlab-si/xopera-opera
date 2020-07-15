import pytest

from opera.error import ParseError
from opera.parser.tosca.timestamp import Timestamp
from opera.parser.yaml.node import Node


class TestValidate:
  @pytest.mark.parametrize("timestamp", [
      "2001-12-15T02:59:43.1Z", "2001-12-14t21:59:43.10-05:00", "2001-12-15 2:59:43.10",
      "2002-12-14", "2022-04-08T21:59:43.10-06:00",
  ])
  def test_valid_timestamp(self, timestamp):
      Timestamp.validate(Node(timestamp))

  @pytest.mark.parametrize("timestamp", [
      "", " ", "trash", "1", "-50", "01.01", "2001-12-15T02:59:43.1ZNJ", "20020-311-31",
      "2001-12-15 50:590?43.10", "-100-12-15 2:59:43.10", "2020-1l0-05-15T00:00:00Z"
  ])
  def test_invalid_timestamp(self, timestamp):
      with pytest.raises(ParseError, match="timestamp"):
          Timestamp.validate(Node(timestamp))
