from .string import String
from .type import Type


class ReferenceWrapper(String):
    def __init__(self, data, loc):
        super().__init__(data, loc)
        self.section_path = ()

    def resolve_reference(self, service_template):
        assert self.section_path, "Missing section path"

        # Special case for root types that should have no parent
        if self.data == "tosca.entity.Root":
            return None

        target = service_template.dig(*self.section_path, self.data)
        if not target:
            self.abort("Invalid reference {}".format(
                "/".join(self.section_path + (self.data,)),
            ), self.loc)

        return target


class DataTypeReferenceWrapper(ReferenceWrapper):
    def resolve_reference(self, service_template):
        if Type.is_valid_internal_type(self.data):
            return Type(self.data, self.loc)
        return super().resolve_reference(service_template)


class Reference:
    WRAPPER_CLASS = ReferenceWrapper

    def __init__(self, *section_path):
        assert section_path, "Section path should not be empty"
        for part in section_path:
            assert isinstance(part, str), \
                "Section path parts should be strings."

        self.section_path = section_path

    def parse(self, yaml_node):
        ref = self.WRAPPER_CLASS.parse(yaml_node)
        ref.section_path = self.section_path
        return ref


class DataTypeReference(Reference):
    WRAPPER_CLASS = DataTypeReferenceWrapper
