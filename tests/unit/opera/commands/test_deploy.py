from opera.commands.deploy import deploy_service_template, deploy_compressed_csar


class TestDeploy:
    def test_deploy_service_template(self, service_template):
        _, path, storage = service_template
        deploy_service_template(path / "service.yaml", {"marker": "test-marker"}, storage, False, 1, True)

    def test_deploy_csar(self, csar):
        path, storage = csar
        deploy_compressed_csar(path / "compressed" / "test.zip", {"marker": "test-marker"}, storage, False, 1, True)
