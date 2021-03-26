# type: ignore

import collections

from opera.constants import StandardInterfaceOperation, ConfigureInterfaceOperation


class DefinitionCollectorMixin:
    def collect_types(self, service_ast):
        parent = self.derived_from.resolve_reference(service_ast)
        if not parent:
            return ()
        return (self.derived_from.data,) + parent.collect_types(service_ast)

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
            defs.update(parent._collect_definitions(section, service_ast))  # pylint: disable=protected-access
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

        standard_interface_names = [StandardInterfaceOperation.shorthand_name(),
                                    StandardInterfaceOperation.type_uri()]
        configure_interface_names = [ConfigureInterfaceOperation.shorthand_name(),
                                     ConfigureInterfaceOperation.type_uri()]

        for name, definition in self.get("interfaces", {}).items():
            if name in standard_interface_names:
                valid_standard_interface_operation_names = [i.value for i in StandardInterfaceOperation]
                for operation in definition.get("operations", {}):
                    if operation not in valid_standard_interface_operation_names:
                        self.abort("Invalid operation for {} interface: {}. Valid operation names are: {}."
                                   .format(name, operation, valid_standard_interface_operation_names), self.loc)

            if name in configure_interface_names:
                valid_configure_interface_operation_names = [i.value for i in ConfigureInterfaceOperation]
                for operation in definition.get("operations", {}):
                    if operation not in valid_configure_interface_operation_names:
                        self.abort("Invalid operation for {} interface: {}. Valid operation names are: {}."
                                   .format(name, operation, valid_configure_interface_operation_names), self.loc)

            # collect operations and inputs from linked interface_types
            # do this only when type is specified and interface name is not Standard or Configure
            if definition.get("type", None) and name not in standard_interface_names + configure_interface_names:
                parent_interface_type = definition.type.resolve_reference(service_ast)
                if parent_interface_type:
                    defs[name]["inputs"].update(parent_interface_type.get("inputs", {}))
                    defs[name]["operations"].update(parent_interface_type.get("operations", {}))

            defs[name]["inputs"].update(definition.get("inputs", {}))
            defs[name]["operations"].update(definition.get("operations", {}))

        return dict(defs)

    def collect_artifact_definitions(self, service_ast):
        return self._collect_definitions("artifacts", service_ast)

    def collect_target_definitions(self, service_ast):
        return {target.data: target for target in self.get("targets", [])}

    def collect_trigger_definitions(self, service_ast):
        return self._collect_definitions("triggers", service_ast)
