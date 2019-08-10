from .string import String


class ReferenceWrapper(String):
    def __init__(self, data, loc):
        super().__init__(data, loc)
        self.section_path = ()


class Reference:
    def __init__(self, *section_path):
        assert section_path, "Section path should not be empty"
        for part in section_path:
            assert isinstance(part, str), \
                "Section path parts should be strings."

        self.section_path = section_path

    def parse(self, yaml_node):
        ref = ReferenceWrapper.parse(yaml_node)
        ref.section_path = self.section_path
        return ref
