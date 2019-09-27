import importlib
import pathlib
from typing import Generic, TypeVar, Type

from opera.csar import ToscaCsar
from opera.error import ParseError
from opera.log import get_logger
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

logger = get_logger()


class ToscaParser(Generic[TDocument]):
    @classmethod
    def parse(cls, csar: ToscaCsar) -> TDocument:
        logger.info("Parsing TOSCA CSAR contents.")
        tosca_version = cls._get_tosca_version(csar)
        logger.debug("Got TOSCA version %s.", tosca_version)
        document_type: Type[TDocument] = cls._get_document_type(tosca_version)
        logger.debug("Got TOSCA document type: %s", document_type)

        parser = ToscaParser(tosca_version, document_type)
        logger.debug("Loading standard library.")
        parser._load_stdlib(tosca_version)  # pylint: disable=protected-access

        service_template = csar.get_service_template()
        # pylint: disable=protected-access
        tosca_document_parsed = parser._parse_csar_file(csar, ToscaPath(service_template,
                                                                        Location(service_template.name, 0, 0)))
        result = parser.stdlib
        logger.debug("Merging parsed document and the TOSCA standard library.")
        result.merge(tosca_document_parsed)
        logger.debug("Resolving node references.")
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
        :param tosca_path: the TOSCA path definition. relative to the CSAR root.
                           If not present, the CSAR service definition file will be used.
        """
        path: pathlib.PurePath = tosca_path.data
        if path.is_absolute():
            return self._parse_bare_file(tosca_path)
        logger.debug("Parsing CSAR file %s.", path)

        with csar.open_member(path) as input_fd:
            tosca_document_yaml = yaml.load(input_fd, path.name)

        if not isinstance(tosca_document_yaml.value, dict):
            raise ParseError("The top level structure must be a map.", tosca_document_yaml.loc)

        tosca_document_parsed = self.document_type.parse(tosca_document_yaml)
        logger.debug("Merging imports from CSAR file %s", path)
        self._merge_imports(csar, tosca_document_parsed)

        return tosca_document_parsed

    def _parse_bare_file(self, tosca_path: ToscaPath) -> TDocument:
        """
        Parses a bare file, not contained in the CSAR.
        :param tosca_path: the TOSCA path reference.
        """
        path: pathlib.PurePath = tosca_path.data
        logger.debug("Parsing bare file %s.", path)
        if not path.is_absolute():
            tosca_path.abort("CSAR-external absolute path '{}' is not absolute.".format(path), tosca_path.loc)

        with open(pathlib.Path(path), "r") as f:
            tosca_document_yaml = yaml.load(f, path.name)
        tosca_document_parsed = self.document_type.parse(tosca_document_yaml)

        # we don't merge imports because this is a bare file
        return tosca_document_parsed

    def _load_stdlib(self, tosca_version: str) -> TDocument:
        stdlib_yaml = stdlib.load(tosca_version)
        return self.document_type.parse(stdlib_yaml)

    def _merge_imports(self, csar: ToscaCsar, document: TDocument):
        """
        Import paths can be absolute or relative.
          - absolute paths can be anywhere on the disk
          - relative paths must exist in the CSAR

        Recursively calls self._parse_*.
        """
        for import_def in document.data.get("imports", []):  # type: ImportDefinition
            import_def_tosca_path: ToscaPath = import_def.file
            import_def_pure_path: pathlib.PurePath = import_def_tosca_path.data

            if import_def_pure_path.is_absolute():
                ToscaParser._validate_absolute_path(import_def_tosca_path)
                parsed_import = self._parse_bare_file(import_def_tosca_path)
            else:
                parsed_import = self._parse_csar_file(csar, import_def_tosca_path)

            document.merge(parsed_import)

        # We do not need imports anymore, since they are preprocessor
        # constructs and would only clutter the AST.
        document.data.pop("imports", None)

    @staticmethod
    def _validate_absolute_path(tosca_path: ToscaPath):
        """
        Validates absolute paths.
        Relative paths are only allowed to be inside CSARs,
        those are validated in DirectoryToscaCsar::_path_within_bounds and ZipToscaCsar::open_member.
        """
        assert tosca_path.data.is_absolute()

        disk_path = pathlib.Path(tosca_path.data).resolve()

        if not disk_path.exists():
            tosca_path.abort("Path '{}' does not exist.".format(str(disk_path)), tosca_path.loc)
        if not disk_path.is_dir() and not disk_path.is_file():
            tosca_path.abort("Path is not file or folder.", tosca_path.loc)

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
