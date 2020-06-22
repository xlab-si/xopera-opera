import collections


class DefinitionCollectorMixin:
    def collect_types(self, service_ast):
        parent = self.derived_from.resolve_reference(service_ast)
        if not parent:
            return ()
        return (self.derived_from.data, ) + parent.collect_types(service_ast)

    def collect_property_definitions(self, service_ast):
        return self._collect_definitions("properties", service_ast)

    def collect_attribute_definitions(self, service_ast):
        return self._collect_definitions("attributes", service_ast)

    def collect_requirement_definitions(self, service_ast):
        return self._collect_definitions("requirements", service_ast)

    def collect_capability_definitions(self, service_ast):
        return self._collect_definitions("capabilities", service_ast)

    def _collect_definitions(self, section, service_ast):
        defs = {}
        parent = self.derived_from.resolve_reference(service_ast)
        if parent:
            defs.update(parent._collect_definitions(section, service_ast))
        defs.update(self.get(section, {}))
        return defs

    def collect_interface_definitions(self, service_ast):
        defs = collections.defaultdict(lambda: dict(inputs={}, operations={}))

        parent = self.derived_from.resolve_reference(service_ast)
        if parent:
            parent_defs = parent.collect_interface_definitions(service_ast)
            for name, definition in parent_defs.items():
                defs[name]["inputs"].update(definition["inputs"])
                defs[name]["operations"].update(definition["operations"])

        for name, definition in self.get("interfaces", {}).items():
            defs[name]["inputs"].update(definition.get("inputs", {}))
            defs[name]["operations"].update(definition.get("operations", {}))

        return dict(defs)

    def collect_artifact_definitions(self, service_ast):
        return self._collect_definitions("artifacts", service_ast)
