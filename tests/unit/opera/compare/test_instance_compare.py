import pytest

from opera.compare.template_comparer import TemplateComparer, TemplateContext
from opera.compare.instance_comparer import InstanceComparer


class TestInstanceCompare:
    @pytest.fixture
    def template_diff(self, service_template1,
                      service_template2):
        comparer = TemplateComparer()
        context = TemplateContext(service_template1[0],
                                  service_template2[0],
                                  service_template1[2],
                                  service_template2[2])
        equal, diff = comparer.compare_service_template(service_template1[0],
                                                        service_template2[0],
                                                        context)
        return diff

    def test_node_state_comparison(self, service_template1,
                                   service_template2, template_diff):
        comparer = InstanceComparer()
        equal, diff = comparer.compare_topology_template(service_template1[1],
                                                         service_template2[1],
                                                         template_diff)
        assert equal is False
        assert len(diff.changed["nodes"].changed) == 5

        assert "hello-1" in diff.changed["nodes"].changed
        assert "hello-2" in diff.changed["nodes"].changed
        assert "hello-3" in diff.changed["nodes"].changed
        assert "hello-6" in diff.changed["nodes"].changed
        assert "my-workstation" in diff.changed["nodes"].changed

        assert "state" in diff.changed["nodes"].changed["hello-1"].changed
        assert "state" in diff.changed["nodes"].changed["hello-2"].changed
        assert "state" in diff.changed["nodes"].changed["hello-3"].changed
        assert "state" in diff.changed["nodes"].changed["hello-6"].changed
        assert "state" in diff.changed["nodes"] \
            .changed["my-workstation"].changed

    def test_dependency_comparison(self, service_template1,
                                   service_template2, template_diff):
        comparer = InstanceComparer()
        equal, diff = comparer.compare_topology_template(service_template1[1],
                                                         service_template2[1],
                                                         template_diff)
        assert equal is False
        assert len(diff.changed["nodes"].changed) == 5

        assert "hello-6" in diff.changed["nodes"].changed
        assert "my-workstation" in diff.changed["nodes"].changed

        assert "dependencies" in diff.changed["nodes"] \
            .changed["hello-6"].changed
        assert "dependencies" in diff.changed["nodes"] \
            .changed["hello-2"].changed

        assert "dependencies" not in diff.changed["nodes"] \
            .changed["hello-1"].changed
        assert "dependencies" not in diff.changed["nodes"] \
            .changed["hello-3"].changed
        assert "dependencies" not in diff.changed["nodes"] \
            .changed["my-workstation"].changed

    def test_prepare_update(self, service_template1,
                            service_template2, template_diff):
        comparer = InstanceComparer()
        for node1 in service_template1[1].nodes.values():
            node1.set_state("started")
        assert service_template2[1].nodes["my-workstation_0"] \
            .state == "initial"
        equal, diff = comparer.compare_topology_template(service_template1[1],
                                                         service_template2[1],
                                                         template_diff)
        assert equal is False
        comparer.prepare_update(service_template1[1],
                                service_template2[1],
                                diff)

        assert service_template1[1].nodes["my-workstation_0"] \
            .state == "initial"
        assert service_template2[1].nodes["my-workstation_0"] \
            .state == "started"
