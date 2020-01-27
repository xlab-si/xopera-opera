from opera.error import ParseError


class Base:
    @classmethod
    def parse(cls, yaml_node):
        yaml_node = cls.normalize(yaml_node)
        cls.validate(yaml_node)
        return cls.build(yaml_node)

    @classmethod
    def normalize(cls, yaml_node):
        return yaml_node

    @classmethod
    def validate(cls, _yaml_node):
        pass

    @classmethod
    def build(cls, yaml_node):
        return cls(yaml_node.bare, yaml_node.loc)

    @classmethod
    def abort(cls, msg, loc=None):
        raise ParseError("[{}] {}".format(cls.__name__, msg), loc)

    def __init__(self, data, loc):
        self.data = data
        self.loc = loc

    def __str__(self):
        return str(self.data)

    def visit(self, method, *args, **kwargs):
        if hasattr(self, method):
            getattr(self, method)(*args, **kwargs)
