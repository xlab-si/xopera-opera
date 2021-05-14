from opera.commands.deploy import deploy_service_template, deploy_compressed_csar
from opera.commands.outputs import outputs


class TestOutputs:
    def test_outputs_service_template(self, service_template):
        _, path, storage = service_template
        deploy_service_template(path / "service.yaml", {"marker": "test-marker"}, storage, False, 1, True)
        outputs(storage)

    def test_outputs_csar(self, csar):
        path, storage = csar
        deploy_compressed_csar(path / "compressed" / "test.zip", {"marker": "test-marker"}, storage, False, 1, True)
        outputs(storage)
