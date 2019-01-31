from opera import ansible


class Operation(object):
    def __init__(self, instance, implementation, inputs):
        self.instance = instance
        self.implementation = implementation
        self.inputs = inputs

    def run(self):
        host = self.instance.get_host()
        # print("HOST: {}".format(host))
        if not self.implementation:
            return True, {}

        print("    Executing {} ...".format(self.implementation))
        evaled_inputs = {
            k: v.eval(self.instance) for k, v in self.inputs.items()
        }
        status, attrs = ansible.run(
            host, self.implementation.primary.data, evaled_inputs,
        )
        return status == 0, attrs
