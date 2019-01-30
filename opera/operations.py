from __future__ import print_function, unicode_literals

from opera import ansible


class Operation(object):
    def __init__(self, instance, implementation, inputs):
        self.instance = instance
        self.implementation = implementation
        self.inputs = inputs

    def run(self):
        if not self.implementation:
            return True, {}

        evaled_inputs = {
            k: v.eval(self.instance) for k, v in self.inputs.items()
        }
        status, attrs = ansible.run(
            self.implementation.primary.data, evaled_inputs,
        )
        return status == 0, attrs
