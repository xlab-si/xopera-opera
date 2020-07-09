from opera.template.interface import Interface
from opera.template.operation import Operation
from opera.template.capability import Capability
from opera.value import Value


class CollectorMixin:
    def collect_types(self, service_ast):
        typ = self.type.resolve_reference(service_ast)
        return (self.type.data, ) + typ.collect_types(service_ast)

    def collect_properties(self, service_ast):
        typ = self.type.resolve_reference(service_ast)
        definitions = typ.collect_property_definitions(service_ast)
        assignments = self.get("properties", {})

        undeclared_props = set(assignments.keys()) - definitions.keys()
        if undeclared_props:
            self.abort("Invalid properties: {}.".format(
                ", ".join(undeclared_props),
            ), self.loc)

        return {
            name: (assignments.get(name) or definition).get_value(
                definition.get_value_type(service_ast),
            ) for name, definition in definitions.items()
        }

    def collect_attributes(self, service_ast):
        typ = self.type.resolve_reference(service_ast)
        definitions = typ.collect_attribute_definitions(service_ast)
        assignments = self.get("attributes", {})

        undeclared_attrs = set(assignments.keys()) - definitions.keys()
        if undeclared_attrs:
            self.abort("Invalid attributes: {}.".format(
                ", ".join(undeclared_attrs),
            ), self.loc)

        return {
            name: (assignments.get(name) or definition).get_value(
                definition.get_value_type(service_ast),
            ) for name, definition in definitions.items()
        }

    def collect_interfaces(self, service_ast):
        typ = self.type.resolve_reference(service_ast)
        definitions = typ.collect_interface_definitions(service_ast)
        assignments = self.get("interfaces", {})

        undeclared_interfaces = set(assignments.keys()) - definitions.keys()
        if undeclared_interfaces:
            self.abort("Invalid interfaces: {}.".format(
                ", ".join(undeclared_interfaces),
            ), self.loc)

        # Next section is nasty. You have been warned.
        interfaces = {}
        for name, definition in definitions.items():
            assignment = self.dig("interfaces", name) or {}

            defined_operations = definition.get("operations", {})
            assigned_operations = assignment.get("operations", {})
            undeclared_operations = (
                set(assigned_operations.keys()) - defined_operations.keys()
            )
            if undeclared_operations:
                self.abort("Undeclared operations: {}.".format(
                    ", ".join(undeclared_operations),
                ), self.loc)

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
                    self.abort("Undeclared inputs: {}.".format(
                        ", ".join(undeclared_inputs),
                    ), self.loc)

                # Outputs, which define the attribute mapping, come from:
                #  1. inteface operation definition,
                #  2. inteface operation assignment in template section
                outputs = {
                    k: [s.data for s in v.data]
                    for k, v in op_definition.get("outputs", {}).items()
                }
                outputs.update({
                    k: [s.data for s in v.data]
                    for k, v in op_assignment.get("outputs", {}).items()
                })

                # Operation implementation details
                impl = (
                    op_assignment.get("implementation") or
                    op_definition.get("implementation")
                )
                # TODO(@tadeboro): impl can be None here. Fix this.
                timeout, operation_host = 0, None
                if "timeout" in impl:
                    timeout = impl.timeout.data
                if "operation_host" in impl:
                    operation_host = impl.operation_host.data

                operations[op_name] = Operation(
                    op_name,
                    primary=impl.primary.file.data,
                    dependencies=[
                        d.file.data for d in impl.get("dependencies", [])
                    ],
                    inputs=inputs,
                    outputs=outputs,
                    timeout=timeout,
                    host=operation_host,
                )

            interfaces[name] = Interface(name, operations)

        return dict(interfaces)

    def collect_capabilities(self, service_ast):
        typ = self.type.resolve_reference(service_ast)
        definitions = typ.collect_capability_definitions(service_ast)
        assignments = self.get("capabilities", {})

        undeclared_caps = set(assignments.keys()) - definitions.keys()
        if undeclared_caps:
            self.abort("Invalid capabilities: {}.".format(
                ", ".join(undeclared_caps),
            ), self.loc)

        return [Capability(name,
                           assignment.get("properties", None),
                           assignment.get("attributes", None))
                for name, assignment in assignments.items()]
