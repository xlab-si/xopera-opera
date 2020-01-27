from opera.executor import ansible


class Operation:
    def __init__(self, name, primary, dependencies, inputs, timeout, host):
        self.name = name
        self.primary = primary
        self.dependencies = dependencies
        self.inputs = inputs
        self.timeout = timeout
        self.host = host
