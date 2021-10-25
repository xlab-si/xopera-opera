# type: ignore
from opera.constants import OperationHost, StandardInterfaceOperation, ConfigureInterfaceOperation
from opera.error import DataError
from opera.template.capability import Capability
from opera.template.interface import Interface
from opera.template.operation import Operation


class CollectorMixin:
    def collect_types(self, service_ast):
        typ = self.type.resolve_reference(service_ast)
        return (self.type.data,) + typ.collect_types(service_ast)

    def collect_properties(self, service_ast):
        typ = self.type.resolve_reference(service_ast)
        definitions = typ.collect_property_definitions(service_ast)
        assignments = self.get("properties", {})

        undeclared_props = set(assignments.keys()) - definitions.keys()
        if undeclared_props:
            self.abort(f"Invalid properties: {', '.join(undeclared_props)}.", self.loc)

        for key, prop_definition in definitions.items():
            prop_required = prop_definition.get("required", None)
            prop_has_default = prop_definition.get("default", None)
            prop_assignment = assignments.get(key, None)
            if prop_required:
                prop_required = prop_required.data
            else:
                prop_required = True

            if prop_required and not prop_has_default and not prop_assignment:
                self.abort(
                    f"Missing a required property: {key}. If the property is optional please specify this in the "
                    f"definition with 'required: false' or supply its default value using 'default: <value>'.", self.loc
                )

        return {
            name: (assignments.get(name) or definition).get_value(definition.get_value_type(service_ast))
            for name, definition in definitions.items()
        }

    def collect_attributes(self, service_ast):
        typ = self.type.resolve_reference(service_ast)
        definitions = typ.collect_attribute_definitions(service_ast)
        assignments = self.get("attributes", {})

        undeclared_attrs = set(assignments.keys()) - definitions.keys()
        if undeclared_attrs:
            self.abort(f"Invalid attributes: {', '.join(undeclared_attrs)}.", self.loc)
        return {
            name: (assignments.get(name) or definition).get_value(
                definition.get_value_type(service_ast),
            ) for name, definition in definitions.items()
        }

    def collect_interfaces(self, service_ast):  # pylint: disable=too-many-locals
        typ = self.type.resolve_reference(service_ast)
        definitions = typ.collect_interface_definitions(service_ast)
        assignments = self.get("interfaces", {})

        undeclared_interfaces = set(assignments.keys()) - definitions.keys()
        if undeclared_interfaces:
            self.abort(f"Undeclared interfaces: {', '.join(undeclared_interfaces)}.", self.loc)

        # Next section is nasty. You have been warned.
        interfaces = {}
        for name, definition in definitions.items():
            assignment = self.dig("interfaces", name) or {}

            defined_operations = definition.get("operations", {})
            assigned_operations = assignment.get("operations", {})
            undeclared_operations = set(assigned_operations.keys()) - defined_operations.keys()
            if undeclared_operations:
                self.abort(f"Undeclared operations: {', '.join(undeclared_operations)}.", self.loc)

            operations = {}
            for op_name, op_definition in defined_operations.items():
                op_assignment = assigned_operations.get(name, {})
                undeclared_inputs = set()

                # Inputs come from four different sources:
                #   1. interface definition,
                #   2. interface operation definition,
                #   3. interface assignment in template section, and
                #   4. interface operation assignment in template section.
                inputs = {
                    k: v.get_value(v.get_value_type(service_ast))
                    for k, v in definition.get("inputs", {}).items()
                }
                inputs.update({
                    k: v.get_value(v.get_value_type(service_ast))
                    for k, v in op_definition.get("inputs", {}).items()
                })

                for k, v in assignment.get("inputs", {}).items():
                    if k not in inputs:
                        undeclared_inputs.add(k)
                    else:
                        inputs[k] = v.get_value(inputs[k].type)
                for k, v in op_assignment.get("inputs", {}).items():
                    if k not in inputs:
                        undeclared_inputs.add(k)
                    else:
                        inputs[k] = v.get_value(inputs[k].type)

                if undeclared_inputs:
                    self.abort(f"Undeclared inputs: {', '.join(undeclared_inputs)}.", self.loc)

                # Outputs, which define the attribute mapping, come from:
                #  1. interface operation definition,
                #  2. interface operation assignment in template section
                outputs = {
                    k: [s.data for s in v.data]
                    for k, v in op_definition.get("outputs", {}).items()
                }
                outputs.update({
                    k: [s.data for s in v.data]
                    for k, v in op_assignment.get("outputs", {}).items()
                })

                # Operation implementation details
                impl = op_assignment.get("implementation") or op_definition.get("implementation")
                # TODO: when impl is None we also pass that forward to operation objects. Fix this if needed.
                timeout, operation_host = 0, None
                if impl and "timeout" in impl:
                    timeout = impl.timeout.data
                if impl and "operation_host" in impl:
                    operation_host_value = impl.operation_host.data
                    try:
                        operation_host = next(oh for oh in OperationHost if oh.value == operation_host_value)
                    except StopIteration as e:
                        raise DataError(
                            f"Could not find operation host {operation_host_value} in {list(OperationHost)}"
                        ) from e

                operations[op_name] = Operation(
                    op_name,
                    primary=impl.primary.file.data if impl else None,
                    dependencies=[d.file.data for d in impl.get("dependencies", [])] if impl else [],
                    artifacts=[a.data for a in self.collect_artifacts(service_ast).values()],
                    inputs=inputs,
                    outputs=outputs,
                    timeout=timeout,
                    host=operation_host,
                )

            # unify Standard and Configure interfaces with type_uri to use only shorthand_name
            if name == StandardInterfaceOperation.type_uri():
                name = StandardInterfaceOperation.shorthand_name()
            if name == ConfigureInterfaceOperation.type_uri():
                name = ConfigureInterfaceOperation.shorthand_name()

            interfaces[name] = Interface(name, operations)

        return dict(interfaces)

    def collect_capabilities(self, service_ast):
        typ = self.type.resolve_reference(service_ast)
        definitions = typ.collect_capability_definitions(service_ast)
        assignments = self.get("capabilities", {})

        undeclared_caps = set(assignments.keys()) - definitions.keys()
        if undeclared_caps:
            self.abort(f"Invalid capabilities: {', '.join(undeclared_caps)}.", self.loc)

        return [
            Capability(name, assignment.get("properties", None), assignment.get("attributes", None))
            for name, assignment in assignments.items()
        ]

    def collect_artifacts(self, service_ast):
        typ = self.type.resolve_reference(service_ast)
        definitions = typ.collect_artifact_definitions(service_ast)
        assignments = self.get("artifacts", {})

        duplicate_interfaces = set(assignments.keys()).intersection(
            definitions.keys())
        if duplicate_interfaces:
            for duplicate in duplicate_interfaces:
                definitions.pop(duplicate)

        definitions.update(assignments)

        return {
            name: (assignments.get(name) or definition).get_value(
                definition.get_value_type(service_ast),
            ) for name, definition in definitions.items()
        }
