import itertools
import abc
from typing import Union

from opera.constants import NodeState, OperationHost, StandardInterfaceOperation, ConfigureInterfaceOperation
from opera.error import DataError, OperationError
from opera.value import Value
from opera.executors.ansible import ansible
from opera.threading import utils as thread_utils


class Base:
    def __init__(self, template, topology, instance_id):
        self.template = template
        self.topology = topology

        # Set attributes that all instances should have
        self.attributes = dict(
            tosca_name=Value(None, True, template.name),
            tosca_id=Value(None, True, instance_id),
            state=Value(None, True, NodeState.INITIAL.value),
        )

        self.reset_attributes()

    def reset_attributes(self):
        # We need to copy values because each instance has a separate set of
        # data. Shared stuff is left in the template. We also make every
        # property into an attribute as TOSCA standard requires.
        self.attributes.update(
            (k, v.copy())
            for k, v in itertools.chain(self.template.properties.items(), self.template.attributes.items())
            if k not in ("tosca_name", "tosca_id", "state")
        )

    def write(self):
        self.topology.write(self.dump(), self.tosca_id)

    def read(self):
        try:
            self.load(self.topology.read(self.tosca_id))
        except FileNotFoundError:
            pass  # There is no state on initial run.

    def dump(self):
        return {k: v.dump() for k, v in self.attributes.items()}

    def load(self, data):
        for k, v in data.items():
            self.attributes[k].load(v)

    @property
    def tosca_name(self):
        return self.attributes["tosca_name"].data

    @property
    def tosca_id(self):
        return self.attributes["tosca_id"].data

    @property
    def state(self):
        state_value = self.attributes["state"].data
        try:
            return next(s for s in NodeState if s.value == state_value)
        except StopIteration as e:
            raise DataError(f"Could not find state {state_value} in {list(NodeState)}") from e

    def set_state(self, state: NodeState, write=True):
        self.set_attribute("state", state.value)
        if write:
            self.write()

    def run_operation(self,
                      host: OperationHost,
                      interface: str,
                      operation_type: Union[StandardInterfaceOperation, ConfigureInterfaceOperation],
                      verbose: bool,
                      workdir: str,
                      validate: bool = False):
        if isinstance(operation_type, (StandardInterfaceOperation, ConfigureInterfaceOperation)):
            operation = self.template.interfaces[interface].operations.get(operation_type.value)
        else:
            operation = self.template.interfaces[interface].operations.get(operation_type)

        if operation:
            success, outputs, attributes = self.run(operation, host, verbose, workdir, validate)
        else:
            success, outputs, attributes = True, {}, {}

        if not success:
            self.set_state(NodeState.ERROR)
            raise OperationError("Failed", self.tosca_name, interface, operation)

        for params, value in outputs:
            self.map_attribute(params, value)
        self.update_attributes(attributes)
        self.write()

    def update_attributes(self, outputs):
        for name, value in outputs.items():
            self.set_attribute(name, value)

    def set_attribute(self, name, value):
        # TODO: Add type validation.
        if name not in self.attributes:
            raise DataError(
                f"Instance has no '{name}' attribute. Available attributes: {', '.join(self.attributes.keys())}"
            )
        self.attributes[name].set(value)

    @abc.abstractmethod
    def get_host(self, host: OperationHost):
        return None

    @abc.abstractmethod
    def map_attribute(self, params, value):
        pass

    def run(self, operation, host: OperationHost, verbose, workdir, validate):
        # TODO: Respect the timeout option.
        # TODO: Add host validation.
        # TODO: Properly handle SELF - not even sure what this proper way would be at this time.
        actual_host = self.get_host(operation.host or host)

        operation_inputs = {k: v.eval(self, k) for k, v in operation.inputs.items()}

        # TODO: Currently when primary is None we skip running the operation. Fix this if needed.
        if not operation.primary:
            return True, {}, {}

        # TODO: We print output only when primary is defined so we can run something. Fix this if needed.
        thread_utils.print_thread(f"    Executing {operation.name} on {self.tosca_id}")

        # TODO: Generalize executors.
        success, ansible_outputs = ansible.run(
            actual_host, str(operation.primary),
            tuple(str(i) for i in operation.dependencies),
            tuple(str(i) for i in operation.artifacts), operation_inputs, verbose,
            workdir, validate
        )
        if not success:
            return False, {}, {}

        outputs = []
        unresolved_outputs = []

        for output, attribute_mapping in operation.outputs.items():
            if output in ansible_outputs:
                outputs.append((attribute_mapping, ansible_outputs[output]))
                ansible_outputs.pop(output)
            else:
                unresolved_outputs.append(output)

        if len(unresolved_outputs) > 0:
            raise DataError(
                f"Operation did not return the following outputs: {', '.join(unresolved_outputs)}")

        return success, outputs, ansible_outputs
