from opera.commands.validate import validate_csar, validate_service_template


class TestValidate:
    def test_validate_service_template(self, service_template):
        _, path, _ = service_template
        validate_service_template(path / "service.yaml", {"marker": "test-marker"})

    def test_validate_directory_based_csar(self, csar):
        path, _ = csar
        validate_csar(path, {"marker": "test-marker"})

    def test_validate_compressed_csar(self, csar):
        path, _ = csar
        validate_csar(path / "compressed" / "test.zip", {"marker": "test-marker"})
