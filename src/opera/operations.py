from typing import Dict, Tuple

from opera import ansible
from opera.instances import Instance
from opera.log import get_logger

logger = get_logger()


class Operation:
    def __init__(self, instance: Instance, implementation, inputs):
        self.instance = instance
        self.implementation = implementation
        self.inputs = inputs

    def run(self) -> Tuple[bool, Dict]:
        host = self.instance.get_host()
        if not host:
            # TODO: static typing allows this to be reachable, investigate which optional is incorrect
            raise Exception("This should not happen.")
        logger.debug("HOST: %s", host)
        if not self.implementation:
            return True, {}

        logger.info("    Executing %s ...", self.implementation)
        evaled_inputs = {
            k: v.eval(self.instance) for k, v in self.inputs.items()
        }
        status, attrs = ansible.run(
            host, self.implementation.primary.data, evaled_inputs,
        )
        return status == 0, attrs
