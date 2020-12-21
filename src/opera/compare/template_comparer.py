import filecmp

from os import path
from .diff import Diff

from .comparisons import Comparison, ListComparison, MapComparison
from opera.error import DataError


class TemplateContext:
    def __init__(self, template1, template2, workdir1, workdir2):
        self.template1 = template1
        self.template2 = template2
        self.workdir1 = workdir1
        self.workdir2 = workdir2


class TemplateComparer:
    def compare_service_template(self, service_template1, service_template2,
                                 context):
        comparisons = {
            "nodes": MapComparison(self._compare_node),
        }
        return self._compare_item(service_template1, service_template2,
                                  comparisons, context)

    def _compare_node(self, node1, node2, context):
        comparisons = {
            "types": Comparison(self._compare_types),
            "properties": MapComparison(self._compare_value),
            "attributes": MapComparison(self._compare_none),
            "requirements": ListComparison(self._compare_requirement,
                                           self._get_name),
            "capabilities": ListComparison(self._compare_capability,
                                           self._get_name),
            "interfaces": MapComparison(self._compare_interface),
        }
        new_context = TemplateContext(node1, node2,
                                      context.workdir1, context.workdir2)
        return self._compare_item(node1, node2, comparisons, new_context)

    def _compare_requirement(self, req1, req2, context):
        comparisons = {
            "target": Comparison(self._compare_target),
            "relationship": Comparison(self._compare_relationship)
        }
        return self._compare_item(req1, req2, comparisons, context)

    def _compare_capability(self, capability1, capability2, context):
        comparisons = {
            "properties": MapComparison(self._compare_capability_property),
            "attributes": MapComparison(self._compare_none)
        }
        return self._compare_item(capability1, capability2, comparisons,
                                  context)

    def _compare_relationship(self, rel1, rel2, context):
        comparisons = {
            "types": Comparison(self._compare_types),
            "properties": MapComparison(self._compare_value),
            "attributes": MapComparison(self._compare_none),
            "interfaces": MapComparison(self._compare_interface)
        }
        new_context = TemplateContext(rel1, rel2,
                                      context.workdir1, context.workdir2)
        return self._compare_item(rel1, rel2,
                                  comparisons,
                                  new_context)

    def _compare_interface(self, interface1, interface2, context):
        comparisons = {
            "operations": MapComparison(self._compare_operation)
        }
        return self._compare_item(interface1, interface2, comparisons, context)

    def _compare_operation(self, operation1, operation2, context):
        comparisons = {
            "primary": Comparison(self._compare_file),
            "inputs": MapComparison(self._compare_value),
            "dependencies": ListComparison(self._compare_file,
                                           self._get_filename),
            "artifacts": ListComparison(self._compare_file,
                                        self._get_filename)
        }
        return self._compare_item(operation1, operation2, comparisons, context)

    def _compare_item(self, item1, item2, comparisons, context):
        diff = Diff()
        for name, comparison in comparisons.items():
            equal = True
            if isinstance(comparison, Comparison):
                equal, change = comparison.compare(getattr(item1, name),
                                                   getattr(item2, name),
                                                   context)
            if not equal:
                diff.changed[name] = change
        return diff.equal(), diff

    def _compare_value(self, val1, val2, context):
        try:
            eval1 = val1.eval(context.template1, "")
        except DataError:
            eval1 = None
        try:
            eval2 = val2.eval(context.template2, "")
        except DataError:
            eval2 = None
        return eval1 == eval2, [eval1, eval2]

    def _compare_types(self, types1, types2, context):
        type1 = types1[0]
        type2 = types2[0]
        return type1 == type2, [type1, type2]

    def _compare_capability_property(self, prop1, prop2, context):
        return prop1.data == prop2.data, [prop1.data, prop2.data]

    def _compare_none(self, attr1, attr2, context):
        # do not compare attribute values
        return True, ""

    def _compare_target(self, target1, target2, context):
        return target1.name == target2.name, [target1.name, target2.name]

    def _compare_file(self, filepath1, filepath2, context):
        equal = filecmp.cmp(path.join(context.workdir1, filepath1),
                            path.join(context.workdir2, filepath2),
                            shallow=False)
        return equal, "file {0}".format(filepath1)

    def _get_filename(self, filepath):
        return str(filepath)

    def _get_name(self, item):
        return item.name
