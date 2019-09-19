from typing import Dict, Tuple

from opera import ansible
from opera.instances import Instance


class Operation(object):
    def __init__(self, instance: Instance, implementation, inputs):
        self.instance = instance
        self.implementation = implementation
        self.inputs = inputs

    def run(self) -> Tuple[bool, Dict]:
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
