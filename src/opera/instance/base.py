import itertools

from opera.error import DataError, OperationError
from opera.value import Value


class Base:
    def __init__(self, template, instance_id):
        self.template = template
        self.topology = None  # Set once we are added to topology.

        # Set attributes that all instances should have
        self.attributes = dict(
            tosca_name=Value(None, True, template.name),
            tosca_id=Value(None, True, instance_id),
            state=Value(None, True, "initial"),
        )

        self.reset_attributes()

    def reset_attributes(self):
        # We need to copy values because each instance has a separate set of
        # data. Shared stuff is left in the template. We also make every
        # property into an attribute as TOSCA standard requires.
        self.attributes.update(
            (k, v.copy()) for k, v in itertools.chain(
                self.template.properties.items(),
                self.template.attributes.items(),
            ) if k not in ("tosca_name", "tosca_id", "state")
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
        return self.attributes["state"].data

    def set_state(self, state):
        self.set_attribute("state", state)
        self.write()

    def run_operation(self, host, interface, operation):
        success, outputs, attributes = self.template.run_operation(
            host, interface, operation, self,
        )

        if not success:
            raise OperationError("Failed")

        for params, value in outputs:
            self.map_attribute(params, value)
        self.update_attributes(attributes)
        self.write()

    def update_attributes(self, outputs):
        for name, value in outputs.items():
            self.set_attribute(name, value)

    def set_attribute(self, name, value):
        # TODO(@tadeboro): Add type validation.
        if name not in self.attributes:
            raise DataError("Instance has no '{}' attribute".format(name))
        self.attributes[name].set(value)
