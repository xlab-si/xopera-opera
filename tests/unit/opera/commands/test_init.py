from opera.commands.init import init_service_template, init_compressed_csar


class TestInit:
    def test_init_service_template(self, service_template):
        _, path, storage = service_template
        init_service_template(path / "service.yaml", {"marker": "test-marker"}, storage, False)

    def test_init_csar(self, csar):
        path, storage = csar
        init_compressed_csar(path / "compressed" / "test.zip", {"marker": "test-marker"}, storage, False)
