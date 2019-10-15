import abc
import pathlib
import zipfile
from abc import abstractmethod
from typing import List, IO

import opera.parser.yaml as opera_yaml
from opera.error import CsarValidationError, UnsupportedToscaFeatureError, FileOutOfBoundsError


class ToscaCsar(abc.ABC):
    """
    The TOSCA Cloud Service Archive.

    Does not support the service metadata format.
    """
    METADATA_DIRNAME = "TOSCA-Metadata"
    METADATA_FILENAME = "TOSCA.meta"

    @classmethod
    def load(cls, path_string: str, strict: bool) -> "ToscaCsar":
        """Load a CSAR from a .zip, directory or service template.

        :param path_string: The CSAR location.
        :param strict: Whether to validate the CSAR structure and contents.
        """

        print("Loading CSAR from {}".format(path_string))
        path = pathlib.Path(path_string)
        if path.is_file():
            try:
                print("Attempting to use a zipped CSAR.")
                csar: ToscaCsar = ZipToscaCsar(path_string)
            except zipfile.BadZipFile:
                print("File not a zip file, assuming a bare service template.")
                csar = VirtualToscaCsar(path_string)
        elif path.is_dir():
            print("Using a non-standard directory CSAR.")
            csar = DirectoryToscaCsar(path_string)
        else:
            raise CsarValidationError("The CSAR is neither a file nor a directory.", "6.1 (xopera extended)")

        if strict:
            csar.validate()
        return csar

    @abstractmethod
    def members(self) -> List[pathlib.PurePath]:
        """
        Get a list of files and directories with paths relative to the root of the CSAR. Absolute paths not allowed.
        """
        pass

    @abstractmethod
    def open_member(self, path: pathlib.PurePath) -> IO:
        """
        Opens a read-only stream for the file at the specified path.
        """
        pass

    @abstractmethod
    def _member_is_dir(self, member: pathlib.PurePath) -> bool:
        """
        Assumes the path, relative to the CSAR root, exists, and returns whether it is a directory.
        Symlinks are resolved.
        """
        pass

    @abstractmethod
    def _member_is_file(self, member: pathlib.PurePath) -> bool:
        """
        Assumes the path, relative to the CSAR root, exists, and returns whether it is a regular file.
        Symlinks are resolved.
        """

    def get_service_template(self) -> pathlib.PurePath:
        """
        Returns the service template file path. Assumes it exists.
        """
        relative_root = pathlib.PurePath(".")
        return next(f for f in self.members() if f.parent == relative_root and self._member_is_file(f))

    def validate(self):
        """
        Validates the CSAR structure and throws an exception if it does not conform to the specification.
        Does not check service templates or dependencies.
        """
        print("Validating CSAR.")
        files = self.members()

        relative_root = pathlib.PurePath(".")
        if any(f for f in files if
               f.parent == relative_root
               and f.name == ToscaCsar.METADATA_DIRNAME
               and self._member_is_dir(f)):
            raise UnsupportedToscaFeatureError("xopera does not support CSAR structures with a metadata directory.")

        root_files = [f for f in files if f.parent == relative_root and self._member_is_file(f)]
        if len(root_files) != 1:
            raise CsarValidationError("Expected exactly 1 file at the CSAR root, got {}.".format(len(root_files)),
                                      "6.3")

        root_yaml_file = self.get_service_template()
        if not root_yaml_file.name.endswith((".yml", ".yaml")):
            raise CsarValidationError("The root service template file name must end with either '.yml' or '.yaml'.",
                                      "6.1")

        with self.open_member(root_yaml_file) as root_yaml_stream:
            root_yaml_dict = opera_yaml.load(root_yaml_stream, root_yaml_file.name).bare

        mandatory_attributes = [
            ("tosca_definitions_version", "tosca definitions version"),
            ("metadata", "metadata section"),
            ("metadata.template_name", "template name metadata"),
            ("metadata.template_version", "template version metadata")
        ]
        for attribute_path, description in mandatory_attributes:
            try:
                element = root_yaml_dict
                for key in attribute_path.split("."):
                    element = element[key]
            except KeyError:
                raise CsarValidationError(
                    "The CSAR Entry-Definitions file must include the {} value.".format(description),
                    "6.3"
                )
        print("CSAR validation successful.")


class ZipToscaCsar(ToscaCsar):
    def __init__(self, path: str):
        super().__init__()
        self.backing_zip = zipfile.ZipFile(path, mode="r")

    def members(self) -> List[pathlib.PurePath]:
        return [pathlib.PurePath(zi.filename) for zi in self.backing_zip.infolist()]

    def open_member(self, path: pathlib.PurePath) -> IO:
        return self.backing_zip.open(path.name, mode="r")

    def _member_is_dir(self, member: pathlib.PurePath) -> bool:
        return next(
            zi for zi in self.backing_zip.infolist() if zi.filename.rstrip("/") == member.name.rstrip("/")).is_dir()

    def _member_is_file(self, member: pathlib.PurePath) -> bool:
        return not self._member_is_dir(member)


class DirectoryToscaCsar(ToscaCsar):
    """
    A non-standard xopera extension to allow for CSARs to be directories, not only ZIPs.
    """

    def __init__(self, directory_path: str):
        super().__init__()
        self.backing_path = pathlib.Path(directory_path).resolve()

    def members(self) -> List[pathlib.PurePath]:
        # queue loop instead of recursion
        # processed by preorder traversal
        result = []
        remaining = list(self.backing_path.iterdir())
        while remaining:
            member = remaining.pop()
            result.append(pathlib.PurePath(str(member.relative_to(self.backing_path))))
            if member.is_dir():
                remaining.extend(member.iterdir())
        return result

    def open_member(self, path: pathlib.PurePath) -> IO:
        if not self._path_within_bounds(path):
            raise FileOutOfBoundsError(self.backing_path, path)

        return (self.backing_path / path).open(mode="r")

    def _member_is_dir(self, member: pathlib.PurePath) -> bool:
        if not self._path_within_bounds(member):
            raise FileOutOfBoundsError(self.backing_path, member)
        return (self.backing_path / member).is_dir()

    def _member_is_file(self, member: pathlib.PurePath) -> bool:
        if not self._path_within_bounds(member):
            raise FileOutOfBoundsError(self.backing_path, member)
        return (self.backing_path / member).is_file()

    def _path_within_bounds(self, path: pathlib.PurePath) -> bool:
        """
        Validates that the path is within the CSAR bounds.
        :param path: the path relative to the CSAR root.
        """
        try:
            relative_path = (self.backing_path / path).relative_to(self.backing_path)
        except ValueError as e:
            print("Absolute path passed to member open: {}".format(str(e)))
            return False
        return not (len(relative_path.parts) > 0 and relative_path.parts[0] == "..")


class VirtualToscaCsar(DirectoryToscaCsar):
    """A virtual CSAR created when using xopera on a single file."""

    def __init__(self, file_path: str):
        super().__init__(str(pathlib.PurePath(file_path).parent))
        full_path = pathlib.Path(file_path).resolve()
        if not full_path.is_file():
            raise CsarValidationError("File '{}' is not a file.".format(file_path), "n/a")

        self.service_template_file = full_path.relative_to(self.backing_path)

    def get_service_template(self) -> pathlib.PurePath:
        return self.service_template_file

    def validate(self):
        # no guarantees about where this file is, so just skip checking
        print("Skipping virtual CSAR validation.")
