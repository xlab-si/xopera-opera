from opera.commands.diff import diff_instances
from opera.compare.instance_comparer import InstanceComparer
from opera.compare.template_comparer import TemplateComparer


class TestWorkirCompare:
    def test_instance_diff(self, service_template1, service_template2):
        storage_1 = service_template1[3]
        storage_2 = service_template2[3]
        comparer_template = TemplateComparer()
        comparer_instance = InstanceComparer()

        diff = diff_instances(storage_1, service_template1[2],
                              storage_2, service_template2[2],
                              comparer_template, comparer_instance,
                              False)

        assert "hello-1" in diff.changed["nodes"].changed
        assert "hello-2" in diff.changed["nodes"].changed
        assert "hello-3" in diff.changed["nodes"].changed
        assert "hello-6" in diff.changed["nodes"].changed
