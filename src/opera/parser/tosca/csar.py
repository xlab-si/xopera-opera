import shutil
import traceback
from abc import ABC, abstractmethod
from pathlib import Path, PurePath
from tempfile import TemporaryDirectory
from typing import List, IO, Optional
from zipfile import ZipFile

import yaml

from opera.error import ParseError, OperaError
from opera.utils import determine_archive_format


class CsarMeta:
    SUPPORTED_META_FILE_VERSIONS = {"1.1"}
    SUPPORTED_CSAR_VERSIONS = {"1.1"}
    METADATA_PATH = "TOSCA-Metadata/TOSCA.meta"

    KEY_NAME = "Name"
    KEY_CONTENT_TYPE = "Content-Type"
    KEY_TOSCA_META_FILE_VERSION = "TOSCA-Meta-File-Version"
    KEY_CSAR_VERSION = "CSAR-Version"
    KEY_CREATED_BY = "Created-By"
    KEY_ENTRY_DEFINITIONS = "Entry-Definitions"

    REQUIRED_KEYS = {KEY_TOSCA_META_FILE_VERSION, KEY_CSAR_VERSION,
                     KEY_CREATED_BY}

    def __init__(self, name: Optional[str], content_type: Optional[str], tosca_meta_file_version: str,
                 csar_version: str, created_by: str, entry_definitions: Optional[str]):
        self.name = name
        self.content_type = content_type
        self.tosca_meta_file_version = tosca_meta_file_version
        self.csar_version = csar_version
        self.created_by = created_by
        self.entry_definitions = entry_definitions

    @classmethod
    def parse(cls, contents: str) -> "CsarMeta":
        # FIXME: the meta format is not yaml, but it"s close enough to parse a simple file
        parsed = yaml.safe_load(contents)

        for req in CsarMeta.REQUIRED_KEYS:
            if req not in parsed:
                raise ParseError(f"Missing required meta entry: {req}", CsarMeta.METADATA_PATH)

        csar_version = str(parsed[CsarMeta.KEY_CSAR_VERSION])
        if csar_version not in CsarMeta.SUPPORTED_CSAR_VERSIONS:
            raise ParseError(
                f"{CsarMeta.KEY_CSAR_VERSION} {csar_version} is not supported. Supported versions: "
                f"{CsarMeta.SUPPORTED_CSAR_VERSIONS}\".", CsarMeta.METADATA_PATH
            )

        tmf_version = str(parsed[CsarMeta.KEY_TOSCA_META_FILE_VERSION])
        if tmf_version not in CsarMeta.SUPPORTED_META_FILE_VERSIONS:
            raise ParseError(
                f"{CsarMeta.KEY_TOSCA_META_FILE_VERSION} {tmf_version} is not supported. Supported versions: "
                f"{CsarMeta.SUPPORTED_META_FILE_VERSIONS}\".", CsarMeta.METADATA_PATH
            )

        result = CsarMeta(
            name=parsed.get(CsarMeta.KEY_NAME),
            content_type=parsed.get(CsarMeta.KEY_CONTENT_TYPE),
            tosca_meta_file_version=tmf_version,
            csar_version=csar_version,
            created_by=parsed[CsarMeta.KEY_CREATED_BY],
            entry_definitions=parsed.get(CsarMeta.KEY_ENTRY_DEFINITIONS),
        )

        return result

    def render(self) -> str:
        ordered_fields = [
            (CsarMeta.KEY_NAME, self.name),
            (CsarMeta.KEY_CONTENT_TYPE, self.content_type),
            (CsarMeta.KEY_TOSCA_META_FILE_VERSION, self.tosca_meta_file_version),
            (CsarMeta.KEY_CSAR_VERSION, self.csar_version),
            (CsarMeta.KEY_CREATED_BY, self.created_by),
            (CsarMeta.KEY_ENTRY_DEFINITIONS, self.entry_definitions)
        ]

        return "\n".join(f"{k}: {v}" for k, v in ordered_fields if v is not None)

    def to_dict(self) -> dict:
        return {
            CsarMeta.KEY_NAME: self.name,
            CsarMeta.KEY_CONTENT_TYPE: self.content_type,
            CsarMeta.KEY_TOSCA_META_FILE_VERSION: self.tosca_meta_file_version,
            CsarMeta.KEY_CSAR_VERSION: self.csar_version,
            CsarMeta.KEY_CREATED_BY: self.created_by,
            CsarMeta.KEY_ENTRY_DEFINITIONS: self.entry_definitions
        }


class ServiceTemplateMeta:
    KEY_NAME = "template_name"
    KEY_AUTHOR = "template_author"
    KEY_VERSION = "template_version"

    REQUIRED_KEYS = {KEY_NAME, KEY_VERSION}

    def __init__(self, name: str, author: str, version: str):
        self.name = name
        self.author = author
        self.version = version

    @classmethod
    def parse(cls, contents: str) -> "ServiceTemplateMeta":
        parsed = yaml.safe_load(contents)

        if "metadata" not in parsed:
            raise ParseError("Missing required service template metadata.", "")

        for req in ServiceTemplateMeta.REQUIRED_KEYS:
            if req not in parsed["metadata"]:
                raise ParseError(f"Missing required service template meta entry: metadata. {req}", "")

        return ServiceTemplateMeta(
            name=parsed["metadata"][ServiceTemplateMeta.KEY_NAME],
            author=parsed["metadata"].get(ServiceTemplateMeta.KEY_AUTHOR),
            version=parsed["metadata"][ServiceTemplateMeta.KEY_VERSION],
        )

    def to_dict(self) -> dict:
        return {
            ServiceTemplateMeta.KEY_NAME: self.name,
            ServiceTemplateMeta.KEY_AUTHOR: self.author,
            ServiceTemplateMeta.KEY_VERSION: self.version
        }


class CloudServiceArchive(ABC):
    def __init__(self, csar_label):
        self.csar_label = csar_label

    @classmethod
    def create(cls, path: PurePath) -> "CloudServiceArchive":
        resolved_path = Path(path)

        if not resolved_path.exists():
            raise FileNotFoundError(f"File does not exist at {path}")

        if resolved_path.is_file():
            return FileCloudServiceArchive(resolved_path)
        elif resolved_path.is_dir():
            return DirCloudServiceArchive(resolved_path)
        else:
            raise OperaError("CSARs are either regular files or directories.")

    @abstractmethod
    def package_csar(self, output_file, service_template=None, csar_format="zip") -> str:
        pass

    @abstractmethod
    def unpackage_csar(self, output_dir):
        pass

    @abstractmethod
    def members(self) -> List[PurePath]:
        """
        Get a list of files and directories with paths relative to the root of the CSAR.

        Absolute paths not allowed.
        """

    @abstractmethod
    def open_member(self, path: PurePath) -> IO:
        """Open a read-only stream for the file at the specified path."""

    @abstractmethod
    def _member_exists(self, member: PurePath) -> bool:
        """Verify whether the member file exists."""

    @abstractmethod
    def _member_is_dir(self, member: PurePath) -> bool:
        """
        Check whether the member is a directory.

        Assumes the path, relative to the CSAR root, exists, and returns whether it is a directory.
        Symlinks are resolved.
        """

    @abstractmethod
    def _member_is_file(self, member: PurePath) -> bool:
        """
        Check whether the member is a file.

        Assumes the path, relative to the CSAR root, exists, and returns whether it is a regular file.
        Symlinks are resolved.
        """

    def validate_csar(self):
        contains_meta = self._member_exists(PurePath(CsarMeta.METADATA_PATH))
        root_yaml_files = self.get_root_yaml_files()
        contains_single_root_yaml = len(root_yaml_files) == 1

        if not contains_meta:
            if not contains_single_root_yaml:
                raise OperaError(
                    f"When CSAR metadata is not present, there should be exactly one root level YAML file in the root "
                    f"of the CSAR. Files found: {str(root_yaml_files)}."
                )

            try:
                self.parse_service_template_meta(root_yaml_files[0])
            except ParseError as e:
                raise OperaError(
                    f"When CSAR metadata is not present, the single root level YAML file must contain metadata: "
                    f"{str(e)}"
                ) from e

        meta = self.parse_csar_meta()
        if meta is not None and meta.entry_definitions is not None:
            # check if "Entry-Definitions" points to an existing
            # template file in the CSAR
            if not self._member_exists(PurePath(meta.entry_definitions)):
                raise OperaError(
                    f"{meta.entry_definitions} defined with Entry-Definitions in {CsarMeta.METADATA_PATH} does not "
                    f"exist."
                )

    def parse_csar_meta(self) -> Optional[CsarMeta]:
        path = PurePath(CsarMeta.METADATA_PATH)
        if not self._member_exists(path):
            return None

        with self.open_member(path) as f:
            contents = f.read()

        return CsarMeta.parse(contents)

    def parse_service_template_meta(self, service_template_path: PurePath) -> Optional[ServiceTemplateMeta]:
        if not self._member_exists(service_template_path):
            return None

        with self.open_member(service_template_path) as f:
            contents = f.read()

        return ServiceTemplateMeta.parse(contents)

    def get_root_yaml_files(self) -> List[PurePath]:
        all_files = self.members()
        result = [f for f in all_files if len(f.parts) == 1 and (f.match("*.yaml") or f.match("*.yml"))]
        return result

    def get_entrypoint(self) -> Optional[PurePath]:
        meta = self.parse_csar_meta()
        if meta is not None and meta.entry_definitions is not None:
            return PurePath(meta.entry_definitions)

        root_yamls = self.get_root_yaml_files()
        return root_yamls[0]


class FileCloudServiceArchive(CloudServiceArchive):
    def __init__(self, csar_file: Path):
        """csar_file is guaranteed to exist, be absolute, and be a file."""
        super().__init__(str(csar_file.name))
        self.csar_file = csar_file
        self.backing_zip = ZipFile(csar_file, mode="r")  # pylint: disable=consider-using-with

    def package_csar(self, output_file, service_template=None, csar_format="zip") -> str:
        raise NotImplementedError("Repackaging a packaged CSAR is not implemented.")

    def unpackage_csar(self, output_dir):
        csar_format = determine_archive_format(str(self.csar_file))
        shutil.unpack_archive(str(self.csar_file), output_dir, csar_format)

    def members(self) -> List[PurePath]:
        return [PurePath(zi.filename) for zi in self.backing_zip.infolist()]

    def open_member(self, path: PurePath) -> IO:
        return self.backing_zip.open(str(path), mode="r")  # pylint: disable=consider-using-with

    def _member_exists(self, member: PurePath) -> bool:
        try:
            self.backing_zip.getinfo(str(member))
            return True
        except KeyError:
            return False

    def _member_is_dir(self, member: PurePath) -> bool:
        return next(
            zi for zi in self.backing_zip.infolist()
            if zi.filename.rstrip("/") == member.name.rstrip("/")
        ).is_dir()

    def _member_is_file(self, member: PurePath) -> bool:
        return not self._member_is_dir(member)


class DirCloudServiceArchive(CloudServiceArchive):
    def __init__(self, csar_dir: Path):
        """csar_dir is guaranteed to exist and be a file."""
        super().__init__(str(csar_dir.name))
        self.csar_dir = csar_dir

    def package_csar(self, output_file: str, service_template: str = None, csar_format: str = "zip") -> str:
        meta = self.parse_csar_meta()

        try:
            if not service_template:
                root_yaml_files = self.get_root_yaml_files()

                if meta is None and len(root_yaml_files) != 1:
                    raise ParseError(
                        f"You didn't specify the CSAR TOSCA entrypoint with '-t/--service-template' option. Therefore "
                        f"there should be one YAML file in the root of the CSAR to select it as the entrypoint. More "
                        f"than one YAML has been found: {list(map(str, root_yaml_files))}. Please select one of the "
                        f"files as the CSAR entrypoint using '-t/--service-template' flag or remove all the excessive "
                        f"YAML files.", self
                    )
                service_template = root_yaml_files[0].name
            else:
                if not self._member_exists(PurePath(service_template)):
                    raise ParseError(
                        f"The supplied TOSCA service template file '{service_template}' does not exist in folder "
                        f"'{self.csar_dir}'.", self
                    )

            meta = self.parse_csar_meta()
            if meta is not None:

                template_entry = meta.entry_definitions
                if service_template and template_entry != service_template:
                    raise ParseError(
                        f"The file entry '{template_entry}' defined within 'Entry-Definitions' in "
                        f"'TOSCA-Metadata/TOSCA.meta' does not match with the file name '{service_template}' supplied "
                        f"in service_template CLI argument.", self
                    )

                # check if "Entry-Definitions" points to an existing
                # template file in the CSAR
                if template_entry is not None and not self._member_exists(PurePath(template_entry)):
                    raise ParseError(
                        f"The file '{template_entry}' defined within 'Entry-Definitions' in "
                        f"'TOSCA-Metadata/TOSCA.meta' does not exist.", self
                    )
                return shutil.make_archive(output_file, csar_format, self.csar_dir)
            else:
                with TemporaryDirectory(prefix="opera-package-") as tempdir:
                    extract_path = Path(tempdir) / "extract"
                    shutil.copytree(self.csar_dir, extract_path)

                    # create TOSCA-Metadata/TOSCA.meta file using the specified
                    # TOSCA service template or directory root YAML file
                    content = (
                        f"TOSCA-Meta-File-Version: 1.1\n"
                        f"CSAR-Version: 1.1\n"
                        f"Created-By: xOpera TOSCA orchestrator\n"
                        f"Entry-Definitions: {service_template}\n"
                    )

                    meta_file_folder = extract_path / "TOSCA-Metadata"
                    meta_file = (meta_file_folder / "TOSCA.meta")

                    meta_file_folder.mkdir()
                    meta_file.touch()
                    meta_file.write_text(content, encoding="utf-8")

                    return shutil.make_archive(output_file, csar_format, extract_path)
        except Exception as e:  # noqa: W0703
            raise ParseError(f"Error creating CSAR:\n{traceback.format_exc()}", self) from e

    def unpackage_csar(self, output_dir):
        raise OperaError("Cannot unpackage a directory-based CSAR.")

    def members(self) -> List[PurePath]:
        # queue loop instead of recursion
        # processed by preorder traversal
        result = []
        remaining = list(self.csar_dir.iterdir())
        while remaining:
            member = remaining.pop()
            result.append(PurePath(str(member.relative_to(self.csar_dir))))
            if member.is_dir():
                remaining.extend(member.iterdir())
        return result

    def open_member(self, path: PurePath) -> IO:
        return (self.csar_dir / path).open(mode="r")

    def _member_exists(self, member: PurePath) -> bool:
        absolute_path = self.csar_dir / member
        return absolute_path.exists()

    def _member_is_dir(self, member: PurePath) -> bool:
        return (self.csar_dir / member).is_dir()

    def _member_is_file(self, member: PurePath) -> bool:
        return (self.csar_dir / member).is_file()
