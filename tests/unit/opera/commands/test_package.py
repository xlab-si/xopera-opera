from opera.commands.package import package


class TestPackage:
    def test_package_service_template(self, service_template):
        _, path, _ = service_template
        package(path, path / "test", path / "service.yaml", "zip")
