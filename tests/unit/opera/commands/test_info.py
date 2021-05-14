from opera.commands.info import info


class TestInfo:
    def test_info_service_template(self, service_template):
        _, path, storage = service_template
        info(path, storage)

    def test_info_csar(self, csar):
        path, storage = csar
        info(path / "compressed" / "test.zip", storage)
