from opera.executor import ansible


class Operation:
    def __init__(self, name, primary, dependencies, inputs, timeout, host):
        self.name = name
        self.primary = primary
        self.dependencies = dependencies
        self.inputs = inputs
        self.timeout = timeout
        self.host = host

    def run(self, host, instance):
        print("    Executing {} on {}".format(self.name, instance.tosca_id))

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
            k: v.eval(instance) for k, v in self.inputs.items()
        }

        # TODO(@tadeboro): Generalize executors.
        return ansible.run(
            actual_host, str(self.primary),
            tuple(str(i) for i in self.dependencies), operation_inputs,
        )
