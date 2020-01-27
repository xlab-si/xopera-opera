from .string import String


class Type(String):
    INTERNAL_TYPES = {
        # YAML 1.2 types
        "string", "integer", "float", "boolean", "null",

        # TOSCA types
        "timestamp", "version", "range", "list", "map", "scalar-unit.size",
        "scalar-unit.time", "scalar-unit.frequency", "scalar-unit.bitrate",
    }

    @classmethod
    def is_valid_internal_type(cls, typ):
        return typ in cls.INTERNAL_TYPES
