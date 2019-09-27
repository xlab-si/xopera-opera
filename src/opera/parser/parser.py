import importlib
import pathlib
from typing import Generic, TypeVar, Type

from opera.csar import ToscaCsar
from opera.error import ParseError
from opera.parser import yaml
from opera.parser.tosca import stdlib
from opera.parser.tosca.map import MapWrapper
from opera.parser.tosca.path import ToscaPath
from opera.parser.tosca.v_1_3.import_definition import ImportDefinition
from opera.parser.utils.location import Location

# TODO: make this into an enum
SUPPORTED_VERSIONS = dict(
    tosca_simple_yaml_1_3="v_1_3",
)

TDocument = TypeVar("TDocument", bound=MapWrapper)


class ToscaParser(Generic[TDocument]):
    @classmethod
    def parse(cls, csar: ToscaCsar) -> TDocument:
        print("Parsing TOSCA CSAR contents.")
        tosca_version = cls._get_tosca_version(csar)
        print("Got TOSCA version %s.", tosca_version)
        document_type: Type[TDocument] = cls._get_document_type(tosca_version)
        print("Got TOSCA document type: %s", document_type)

        parser = ToscaParser(tosca_version, document_type)
        print("Loading standard library.")
        parser._load_stdlib(tosca_version)  # pylint: disable=protected-access

        service_template = csar.get_service_template()
        # pylint: disable=protected-access
        tosca_document_parsed = parser._parse_csar_file(csar, ToscaPath(service_template,
                                                                        Location(service_template.name, 0, 0)))
        result = parser.stdlib
        print("Merging parsed document and the TOSCA standard library.")
        result.merge(tosca_document_parsed)
        print("Resolving node references.")
        result.visit("resolve_reference", result)

        return result

    def __init__(self, tosca_version: str, document_type: Type[TDocument]):
        self.tosca_version = tosca_version
        self.document_type = document_type
        self.stdlib: TDocument = self._load_stdlib(self.tosca_version)

    def _parse_csar_file(self, csar: ToscaCsar, tosca_path: ToscaPath) -> TDocument:
        """
        Parse a file contained in a CSAR.
        :param csar: the CSAR file.
        :param tosca_path: the TOSCA path definition, relative to the CSAR root.
        """
        # this path can't be absolute because ToscaPaths have a check for that
        path: pathlib.PurePath = tosca_path.data
        print("Parsing CSAR file %s.", path)

        with csar.open_member(path) as input_fd:
            tosca_document_yaml = yaml.load(input_fd, path.name)

        if not isinstance(tosca_document_yaml.value, dict):
            raise ParseError("The top level structure must be a map.", tosca_document_yaml.loc)

        tosca_document_parsed = self.document_type.parse(tosca_document_yaml)
        print("Merging imports from CSAR file %s", path)
        self._merge_imports(csar, tosca_document_parsed)

        return tosca_document_parsed

    def _load_stdlib(self, tosca_version: str) -> TDocument:
        stdlib_yaml = stdlib.load(tosca_version)
        return self.document_type.parse(stdlib_yaml)

    def _merge_imports(self, csar: ToscaCsar, document: TDocument):
        """
        Import paths can only be relative to the root of the CSAR.

        Recursively calls self._parse_csar_file.
        """
        for import_def in document.data.get("imports", []):  # type: ImportDefinition
            # this path can't be absolute because ToscaPaths have a check for that
            import_def_tosca_path: ToscaPath = import_def.file
            parsed_import = self._parse_csar_file(csar, import_def_tosca_path)
            document.merge(parsed_import)

        # We do not need imports anymore, since they are preprocessor
        # constructs and would only clutter the AST.
        document.data.pop("imports", None)

    @staticmethod
    def _get_document_type(tosca_version: str) -> Type[TDocument]:
        # noinspection PyUnresolvedReferences
        return importlib.import_module("{}.tosca.{}.service_template".format(__package__,  # type: ignore[attr-defined]
                                                                             tosca_version)).ServiceTemplate

    @staticmethod
    def _get_tosca_version(csar: ToscaCsar):
        with csar.open_member(csar.get_service_template()) as f:
            top_level_yaml_node = yaml.load(f, csar.get_service_template().name)

        for k, v in top_level_yaml_node.value.items():
            if k.value == "tosca_definitions_version":
                try:
                    return SUPPORTED_VERSIONS[v.value]
                except (TypeError, KeyError):
                    raise ParseError(
                        "Invalid TOSCA version. Available: {}.".format(", ".join(SUPPORTED_VERSIONS.keys())), v.loc)

        raise ParseError("Missing TOSCA version", top_level_yaml_node.loc)
