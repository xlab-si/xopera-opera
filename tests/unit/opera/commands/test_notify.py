from opera.commands.deploy import deploy_service_template, deploy_compressed_csar
from opera.commands.notify import notify


class TestNotify:
    def test_notify_service_template(self, service_template):
        _, path, storage = service_template
        deploy_service_template(path / "service.yaml", {"marker": "test-marker"}, storage, False, 1, True)
        notify(storage, False, "hello", "")

    def test_notify_csar(self, csar):
        path, storage = csar
        deploy_compressed_csar(path / "compressed" / "test.zip", {"marker": "test-marker"}, storage, False, 1, True)
        notify(storage, False, "hello", "")
