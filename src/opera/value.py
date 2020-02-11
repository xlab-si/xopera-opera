import copy

from opera.error import DataError


class Value:
    FUNCTIONS = frozenset((
        "get_attribute",
        "get_input",
        "get_property",
    ))

    def __init__(self, typ, present, data=None):
        self.type = typ
        self.present = present
        self._data = data

    def dump(self):
        return dict(is_set=self.present, data=self._data)

    def load(self, data):
        self.present = data["is_set"]
        self._data = data["data"]

    @property
    def data(self):
        assert self.present, "Accessing an unset value. Bug-fixing ahead ;)"
        return self._data

    def copy(self):
        return type(self)(self.type, self.present, copy.deepcopy(self._data))

    def set(self, data):
        self._data = data
        self.present = True

    def unset(self):
        self._data = None
        self.present = False

    def eval(self, instance):
        if not self.present:
            raise DataError("Cannot use an unset value.")

        if self.is_function:
            return self.eval_function(instance)
        return self.data

    @property
    def is_function(self):
        return (
            isinstance(self.data, dict) and
            len(self.data) == 1 and
            tuple(self.data.keys())[0] in self.FUNCTIONS
        )

    def eval_function(self, instance):
        (function_name, params), = self.data.items()
        return getattr(instance, function_name)(params)

    def __str__(self):
        return "Value({})[{}]".format(self.present, self._data)
