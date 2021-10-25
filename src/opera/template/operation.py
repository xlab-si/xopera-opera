from opera.constants import OperationHost
from opera.error import DataError
from opera.executor import ansible
from opera.threading import utils as thread_utils


class Operation:
    def __init__(self, name, primary, dependencies, artifacts, inputs, outputs, timeout, host: OperationHost):
        self.name = name
        self.primary = primary
        self.dependencies = dependencies
        self.artifacts = artifacts
        self.inputs = inputs
        self.outputs = outputs
        self.timeout = timeout
        self.host = host

    def run(self, host: OperationHost, instance, verbose, workdir, validate):
        thread_utils.print_thread(f"    Executing {self.name} on {instance.tosca_id}")

        # TODO(@tadeboro): Respect the timeout option.
        # TODO(@tadeboro): Add host validation.
        # TODO(@tadeboro): Properly handle SELF - not even sure what this
        # proper way would be at this time.
        host = self.host or host
        if host in (OperationHost.SELF, OperationHost.HOST):
            actual_host = instance.get_host()
        elif host == OperationHost.SOURCE:
            actual_host = instance.source.get_host()
        elif host == OperationHost.TARGET:
            actual_host = instance.target.get_host()
        else:  # ORCHESTRATOR
            actual_host = "localhost"

        operation_inputs = {k: v.eval(instance, k) for k, v in self.inputs.items()}

        # TODO: Currently when primary is None we skip running the operation. Fix this if needed.
        if not self.primary:
            return True, {}, {}

        # TODO(@tadeboro): Generalize executors.
        success, ansible_outputs = ansible.run(
            actual_host, str(self.primary),
            tuple(str(i) for i in self.dependencies),
            tuple(str(i) for i in self.artifacts), operation_inputs, verbose,
            workdir, validate
        )
        if not success:
            return False, {}, {}

        outputs = []
        unresolved_outputs = []

        for output, attribute_mapping in self.outputs.items():
            if output in ansible_outputs:
                outputs.append((attribute_mapping, ansible_outputs[output]))
                ansible_outputs.pop(output)
            else:
                unresolved_outputs.append(output)

        if len(unresolved_outputs) > 0:
            raise DataError(
                f"Operation did not return the following outputs: {', '.join(unresolved_outputs)}")

        return success, outputs, ansible_outputs
