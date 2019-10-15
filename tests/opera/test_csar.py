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
    VIRTUAL = 3


# https://stackoverflow.com/questions/1855095/
def _zip_directory_contents(contents_path: pathlib.Path, destination_file_path: str):
    with zipfile.ZipFile(destination_file_path, mode="a") as zipf:
        for root, _, files in os.walk(str(contents_path)):
            # don't include the root directory as the dot
            relative_dir_path = os.path.relpath(root, str(contents_path))
            if relative_dir_path != ".":
                zipf.write(root, arcname=relative_dir_path)
            for file in files:
                zipf.write(os.path.join(root, file),
                           arcname=os.path.relpath(os.path.join(root, file), str(contents_path)))


def _base_loader(path: pathlib.Path, mode: CsarTestMode, tmp_path: pathlib.Path):
    if mode == CsarTestMode.ZIP:
        _, tmpfile_path = tempfile.mkstemp(prefix="xoperatmp-", suffix=".zip", dir=str(tmp_path))
        _zip_directory_contents(path, tmpfile_path)
        ToscaCsar.load(tmpfile_path, strict=True)

        # on success, the temp file is deleted
        os.remove(tmpfile_path)
    elif mode == CsarTestMode.DIRECTORY:
        ToscaCsar.load(str(path), strict=True)
    else:
        raise Exception("Unsupported test CSAR mode.")


class TestCsar:
    @pytest.mark.parametrize("mode", [CsarTestMode.ZIP, CsarTestMode.DIRECTORY])
    def test_load_example_mini(self, mode, tmp_path: pathlib.Path):
        _base_loader(_RESOURCE_DIRECTORY / "csar/mini/", mode, tmp_path)

    @pytest.mark.parametrize("mode", [CsarTestMode.ZIP, CsarTestMode.DIRECTORY])
    def test_load_barebones(self, mode, tmp_path: pathlib.Path):
        _base_loader(_RESOURCE_DIRECTORY / "csar/barebones/", mode, tmp_path)

    @pytest.mark.parametrize("mode", [CsarTestMode.ZIP, CsarTestMode.DIRECTORY])
    def test_load_metadata_directory(self, mode, tmp_path: pathlib.Path):
        with pytest.raises(UnsupportedToscaFeatureError):
            _base_loader(_RESOURCE_DIRECTORY / "csar/metadatadir/", mode, tmp_path)

    @pytest.mark.parametrize("mode", [CsarTestMode.ZIP, CsarTestMode.DIRECTORY])
    def test_load_missing_metadata(self, mode, tmp_path: pathlib.Path):
        with pytest.raises(CsarValidationError):
            _base_loader(_RESOURCE_DIRECTORY / "csar/missingmetadata/", mode, tmp_path)

    @pytest.mark.parametrize("mode", [CsarTestMode.ZIP, CsarTestMode.DIRECTORY])
    def test_load_multiple_root_files(self, mode, tmp_path: pathlib.Path):
        with pytest.raises(CsarValidationError):
            _base_loader(_RESOURCE_DIRECTORY / "csar/multipleroot/", mode, tmp_path)

    @pytest.mark.parametrize(
        "where", [
            "../../does/not/exist",
            "../nonexistent",
            "/nonexistent"
            "/nextlevel/nonexistent"
        ]
    )
    def test_load_nonexistent_member_outside_bounds(self, where):
        # this member cannot exist because .members() only returns files inside bounds
        # but the user can still pass any path to the open function
        csar = ToscaCsar.load(str(_RESOURCE_DIRECTORY / "csar/barebones/"), strict=True)
        with pytest.raises(FileOutOfBoundsError):
            csar.open_member(pathlib.PurePath(where))

    def test_load_existent_member_outside_bounds_absolute(self, tmp_path: pathlib.Path):
        csar = ToscaCsar.load(str(_RESOURCE_DIRECTORY / "csar/barebones/"), strict=True)
        _, tmpfile_path = tempfile.mkstemp(prefix="xoperatmp-", suffix=".txt", dir=str(tmp_path))
        absolute_path = pathlib.Path(tmpfile_path).absolute()
        with pytest.raises(FileOutOfBoundsError):
            csar.open_member(pathlib.PurePath(absolute_path))

    def test_load_existent_member_outside_bounds_relative(self, tmp_path: pathlib.Path):
        csar_directory = _RESOURCE_DIRECTORY / "csar/barebones/"
        csar = ToscaCsar.load(str(csar_directory), strict=True)
        _, tmpfile_path = tempfile.mkstemp(prefix="xoperatmp-", suffix=".txt", dir=str(tmp_path))
        relative_path = pathlib.Path(os.path.relpath(tmpfile_path, start=str(csar_directory)))
        with pytest.raises(FileOutOfBoundsError):
            csar.open_member(pathlib.PurePath(relative_path))

    @pytest.mark.parametrize(
        "which", [
            "metadatadir",
            "missingmetadata",
            "multipleroot"
        ]
    )
    def test_nonstrict_success(self, which):
        ToscaCsar.load(_RESOURCE_DIRECTORY / "csar/{}".format(which), strict=False)
