from opera.error import DataError
from opera.executor import ansible
from opera.threading import utils as thread_utils


class Operation:
    def __init__(self, name, primary, dependencies, artifacts, inputs, outputs, timeout, host):
        self.name = name
        self.primary = primary
        self.dependencies = dependencies
        self.artifacts = artifacts
        self.inputs = inputs
        self.outputs = outputs
        self.timeout = timeout
        self.host = host

    def run(self, host, instance, verbose, workdir):
        thread_utils.print_thread(
            "    Executing {} on {}".format(self.name, instance.tosca_id)
        )

        # TODO(@tadeboro): Respect the timeout option.
        # TODO(@tadeboro): Add host validation.
        # TODO(@tadeboro): Properly handle SELF - not even sure what this
        # proper way would be at this time.
        host = self.host or host
        if host in ("SELF", "HOST"):
            actual_host = instance.get_host()
        elif host == "SOURCE":
            actual_host = instance.source.get_host()
        elif host == "TARGET":
            actual_host = instance.target.get_host()
        else:  # ORCHESTRATOR
            actual_host = "localhost"

        operation_inputs = {
            k: v.eval(instance, k) for k, v in self.inputs.items()
        }

        # TODO(@tadeboro): Generalize executors.
        success, ansible_outputs = ansible.run(
            actual_host, str(self.primary),
            tuple(str(i) for i in self.dependencies),
            tuple(str(i) for i in self.artifacts), operation_inputs, verbose,
            workdir
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
                "Operation did not return the following outputs: {}".format(
                    ", ".join(unresolved_outputs)))

        return success, outputs, ansible_outputs
