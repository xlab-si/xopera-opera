from opera.parser.utils.location import Location

class TestStr:
    def test_str(self):
        assert str(Location("stream", 1, 2)) == "stream:1:2"
