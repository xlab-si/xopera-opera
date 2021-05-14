from opera.commands.unpackage import unpackage


class TestUnpackage:
    def test_unpackage_csar(self, csar):
        path, _ = csar
        unpackage(path / "compressed" / "test.zip", path)
