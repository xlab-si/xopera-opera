from opera.commands.validate import validate_csar, validate_service_template


class TestValidate:
    def test_validate_service_template(self, service_template):
        _, path, storage = service_template
        validate_service_template(path / "service.yaml", {"marker": "test-marker"}, storage, False, False)

    def test_validate_directory_based_csar(self, csar):
        path, storage = csar
        validate_csar(path, {"marker": "test-marker"}, storage, False, False)

    def test_validate_compressed_csar(self, csar):
        path, storage = csar
        validate_csar(path / "compressed" / "test.zip", {"marker": "test-marker"}, storage, False, False)
