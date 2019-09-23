import enum
import os
import pathlib
import tempfile
import zipfile

import pytest

from opera.csar import ToscaCsar
from opera.error import CsarValidationError, UnsupportedToscaFeatureError, FileOutOfBoundsError

_RESOURCE_DIRECTORY = pathlib.Path(__file__).parent.parent.absolute() / "resources/"


class CsarTestMode(enum.Enum):
    ZIP = 1
    DIRECTORY = 2


# https://stackoverflow.com/questions/1855095/
def _zip_directory_contents(contents_path: str, destination_file_path: str):
    with zipfile.ZipFile(destination_file_path, mode="a") as zipf:
        for root, dirs, files in os.walk(contents_path):
            # don't include the root directory as the dot
            relative_dir_path = os.path.relpath(root, contents_path)
            if relative_dir_path != ".":
                zipf.write(root, arcname=relative_dir_path)
            for file in files:
                zipf.write(os.path.join(root, file), arcname=os.path.relpath(os.path.join(root, file), contents_path))


def _base_loader(path: str, mode: CsarTestMode):
    if mode == CsarTestMode.ZIP:
        tmpfile, tmpfile_path = tempfile.mkstemp(prefix="xoperatmp-", suffix=".zip")
        _zip_directory_contents(path, tmpfile_path)
        ToscaCsar.load(tmpfile_path)

        # on success, the temp file is deleted
        os.remove(tmpfile_path)
    elif mode == CsarTestMode.DIRECTORY:
        ToscaCsar.load(path)
    else:
        raise Exception("Unsupported test CSAR mode.")


class TestCsar:
    @pytest.mark.parametrize("mode", [CsarTestMode.ZIP, CsarTestMode.DIRECTORY])
    def test_load_example_mini(self, mode):
        _base_loader(_RESOURCE_DIRECTORY / "csar/mini/", mode)

    @pytest.mark.parametrize("mode", [CsarTestMode.ZIP, CsarTestMode.DIRECTORY])
    def test_load_barebones(self, mode):
        _base_loader(_RESOURCE_DIRECTORY / "csar/barebones/", mode)

    @pytest.mark.parametrize("mode", [CsarTestMode.ZIP, CsarTestMode.DIRECTORY])
    def test_load_metadata_directory(self, mode):
        with pytest.raises(UnsupportedToscaFeatureError):
            _base_loader(_RESOURCE_DIRECTORY / "csar/metadatadir/", mode)

    @pytest.mark.parametrize("mode", [CsarTestMode.ZIP, CsarTestMode.DIRECTORY])
    def test_load_missing_metadata(self, mode):
        with pytest.raises(CsarValidationError):
            _base_loader(_RESOURCE_DIRECTORY / "csar/missingmetadata/", mode)

    @pytest.mark.parametrize("mode", [CsarTestMode.ZIP, CsarTestMode.DIRECTORY])
    def test_load_multiple_root_files(self, mode):
        with pytest.raises(CsarValidationError):
            _base_loader(_RESOURCE_DIRECTORY / "csar/multipleroot/", mode)

    @pytest.mark.parametrize("where", ["../../../../../../../../../../../../../../../../etc/hosts", "/etc/hosts"])
    def test_load_member_outside_bounds(self, where):
        # this member cannot exist because .members() only returns files inside bounds
        # but the user can still pass any path to the open function
        csar = ToscaCsar.load(_RESOURCE_DIRECTORY / "csar/barebones/")
        with pytest.raises(FileOutOfBoundsError):
            csar.open_member(pathlib.PurePath(where))
