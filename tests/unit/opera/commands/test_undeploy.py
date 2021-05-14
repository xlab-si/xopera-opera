from opera.commands.deploy import deploy_service_template, deploy_compressed_csar
from opera.commands.undeploy import undeploy


class TestUndeploy:
    def test_undeploy_service_template(self, service_template):
        _, path, storage = service_template
        deploy_service_template(path / "service.yaml", {"marker": "test-marker"}, storage, False, 1, True)
        undeploy(storage, False, 1)

    def test_undeploy_csar(self, csar):
        path, storage = csar
        deploy_compressed_csar(path / "compressed" / "test.zip", {"marker": "test-marker"}, storage, False, 1, True)
        undeploy(storage, False, 1)
