import pytest

from opera.compare.template_comparer import TemplateComparer, TemplateContext


class TestTemplateCompare:
    def test_service_template_comparison(self, service_template1,
                                         service_template2):
        comparer = TemplateComparer()
        context = TemplateContext(service_template1[0],
                                  service_template2[0],
                                  service_template1[2],
                                  service_template2[2])
        equal, diff = comparer.compare_service_template(service_template1[0],
                                                        service_template2[0],
                                                        context)

        assert equal is False

        assert len(diff.changed["nodes"].added) == 1
        assert len(diff.changed["nodes"].deleted) == 1
        assert len(diff.changed["nodes"].changed) == 4

        assert "hello-5" == diff.changed["nodes"].added[0]
        assert "hello-4" == diff.changed["nodes"].deleted[0]

        assert "hello-1" in diff.changed["nodes"].changed
        assert "hello-2" in diff.changed["nodes"].changed
        assert "hello-3" in diff.changed["nodes"].changed
        assert "hello-6" in diff.changed["nodes"].changed
        assert " my-workstation" not in diff.changed["nodes"].changed

    def test_node_comparison(self, service_template1,
                             service_template2):
        comparer = TemplateComparer()
        node1_1 = service_template1[0].get_node("hello-1")
        node2_1 = service_template2[0].get_node("hello-1")
        context = TemplateContext(node1_1, node2_1,
                                  service_template1[2],
                                  service_template2[2])
        equal, diff = comparer._compare_node(node1_1, node2_1, context)

        assert equal is False

        assert "capabilities" in diff.changed
        assert "interfaces" in diff.changed
        assert "properties" in diff.changed
        assert "requirements" not in diff.changed
        assert "types" not in diff.changed

        node1_2 = service_template1[0].get_node("hello-2")
        node2_2 = service_template2[0].get_node("hello-2")
        context = TemplateContext(node1_2, node2_2,
                                  service_template1[2],
                                  service_template2[2])
        equal, diff = comparer._compare_node(node1_2, node2_2, context)

        assert equal is False

        assert "capabilities" in diff.changed
        assert "interfaces" in diff.changed
        assert "properties" in diff.changed
        assert "requirements" in diff.changed
        assert "types" in diff.changed

    def test_requirement_comparison(self, service_template1,
                                    service_template2):
        comparer = TemplateComparer()
        node1 = service_template1[0].get_node("hello-6")
        node2 = service_template2[0].get_node("hello-6")
        context = TemplateContext(node1, node2,
                                  service_template1[2],
                                  service_template2[2])
        equal, diff = comparer._compare_node(node1, node2, context)

        assert equal is False

        assert "requirements" in diff.changed
        assert "dependency" in diff.changed["requirements"].changed
        assert "target" in diff.changed["requirements"] \
            .changed["dependency"].changed

    def test_interface_comparison(self, service_template1,
                                  service_template2):
        comparer = TemplateComparer()
        node1 = service_template1[0].get_node("hello-1")
        node2 = service_template2[0].get_node("hello-1")
        context = TemplateContext(node1, node2,
                                  service_template1[2],
                                  service_template2[2])
        equal, diff = comparer._compare_node(node1, node2, context)

        assert equal is False

        assert "interfaces" in diff.changed
        assert "create" in diff.changed["interfaces"] \
            .changed["Standard"].changed["operations"].changed
        assert "artifacts" in diff.changed["interfaces"] \
            .changed["Standard"].changed["operations"] \
            .changed["create"].changed
        assert "inputs" in diff.changed["interfaces"] \
            .changed["Standard"].changed["operations"] \
            .changed["create"].changed
