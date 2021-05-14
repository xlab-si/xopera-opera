from opera.commands.deploy import deploy_service_template
from opera.commands.diff import diff_instances
from opera.commands.update import update
from opera.compare.instance_comparer import InstanceComparer
from opera.compare.template_comparer import TemplateComparer


class TestUpdate:
    def test_update_service_template(self, service_template, service_template_updated):
        _, path, storage = service_template
        _, path_updated, storage_updated = service_template_updated
        deploy_service_template(path / "service.yaml", {"marker": "test-marker"}, storage, False, 1, True)
        deploy_service_template(path_updated / "service.yaml", {"marker": "test-marker"}, storage_updated, False, 1,
                                True)

        template_comparer = TemplateComparer()
        instance_comparer = InstanceComparer()
        diff = diff_instances(storage, path, storage_updated, path_updated, template_comparer, instance_comparer, False)
        update(storage, path, storage_updated, path_updated, instance_comparer, diff, False, 1, True)
