import copy

from opera.error import DataError


class Value:
    FUNCTIONS = frozenset((
        "get_attribute",
        "get_input",
        "get_property",
        "get_artifact",
        "concat",
        "join",
        "token",
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
        if not self.present:
            raise AssertionError("Accessing an unset value. Bug-fixing ahead ;)")
        return self._data

    def copy(self):
        return type(self)(self.type, self.present, copy.deepcopy(self._data))

    def set(self, data):
        self._data = data
        self.present = True

    def unset(self):
        self._data = None
        self.present = False

    def eval(self, instance, key):
        if not self.present:
            raise DataError("Cannot use an unset value: {}".format(key))

        if self.is_function:
            return Value.eval_function(self.data, instance)

        if isinstance(self.data, dict):
            result_map = {}
            for map_key, value in self.data.items():
                result_map[map_key] = Value.check_eval_function(value, instance)
            return result_map

        if isinstance(self.data, list):
            result_list = []
            for value in self.data:
                result_list.append(Value.check_eval_function(value, instance))
            return result_list

        return self.data

    @property
    def is_function(self):
        return Value.check_function(self.data)

    @staticmethod
    def check_function(data):
        return isinstance(data, dict) and len(data) == 1 and tuple(data.keys())[0] in Value.FUNCTIONS

    @staticmethod
    def eval_function(data, instance):
        (function_name, params), = data.items()
        return getattr(instance, function_name)(params)

    @staticmethod
    def check_eval_function(data, instance):
        if Value.check_function(data):
            return Value.eval_function(data, instance)
        return data

    def __str__(self):
        return "Value({})[{}]".format(self.present, self._data)
