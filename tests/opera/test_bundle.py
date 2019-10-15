import pathlib
import tempfile

import pytest

from opera.bundle import OperaBundle
from opera.error import OperaBundleError, CsarValidationError, UnsupportedToscaFeatureError

_RESOURCE_DIRECTORY = pathlib.Path(__file__).parent.parent.absolute() / "resources/"


class TestBundle:
    def test_init_success_link(self, tmp_path: pathlib.Path):
        bundle_path = tmp_path / "mini"
        csar_path: pathlib.Path = (_RESOURCE_DIRECTORY / "csar/mini/").resolve()
        bundle = OperaBundle.init(bundle_path, csar_path)
        bundle.validate()

        assert (bundle_path / OperaBundle.SUBDIR_CSAR).is_symlink()
        assert (bundle_path / OperaBundle.SUBDIR_CSAR).resolve() == csar_path

    def test_init_success_zip(self, tmp_path: pathlib.Path, zip_directory_contents):
        bundle_path = tmp_path / "mini"
        csar_path: pathlib.Path = (_RESOURCE_DIRECTORY / "csar/mini/").resolve()
        _, zipfile_path = tempfile.mkstemp(prefix="xoperatmp-", suffix=".zip", dir=str(tmp_path))
        zip_directory_contents(csar_path, zipfile_path)

        bundle = OperaBundle.init(bundle_path, pathlib.Path(zipfile_path))
        bundle.validate()

        assert not (tmp_path / OperaBundle.SUBDIR_CSAR).is_symlink()

    def test_init_existing_dir(self, tmp_path: pathlib.Path):
        bundle_path = tmp_path
        csar_path: pathlib.Path = (_RESOURCE_DIRECTORY / "csar/mini/").resolve()
        with pytest.raises(OperaBundleError):
            OperaBundle.init(bundle_path, csar_path)

    def test_init_missing_csar_absolute(self, tmp_path: pathlib.Path):
        bundle_path = tmp_path / "mini"
        csar_path = pathlib.Path("/does/not/exist")
        with pytest.raises(OperaBundleError):
            OperaBundle.init(bundle_path, csar_path)

    def test_init_missing_csar_relative(self, tmp_path: pathlib.Path):
        bundle_path = tmp_path / "mini"
        csar_path = pathlib.Path(tmp_path / "doesnotexist")
        with pytest.raises(OperaBundleError):
            OperaBundle.init(bundle_path, csar_path)

    def test_init_nonzip_csar(self, tmp_path: pathlib.Path):
        bundle_path = tmp_path / "mini"
        csar_path: pathlib.Path = (_RESOURCE_DIRECTORY / "csar/mini/mini.yaml").resolve()
        with pytest.raises(OperaBundleError):
            OperaBundle.init(bundle_path, csar_path)

    @pytest.mark.parametrize("which,strict", [
        tuple
        for which in ["metadatadir", "missingmetadata", "multipleroot"]
        for tuple in [(which, True), (which, False)]
    ])
    def test_load_invalid_csar_strict_nonstrict(self, which, strict, tmp_path: pathlib.Path):
        bundle_path = tmp_path / which
        csar_path: pathlib.Path = (_RESOURCE_DIRECTORY / "csar/{}/".format(which)).resolve()
        OperaBundle.init(bundle_path, csar_path)

        if strict:
            # noinspection PyTypeChecker
            with pytest.raises((CsarValidationError, UnsupportedToscaFeatureError)):
                OperaBundle(bundle_path, strict=strict)
                pass
        else:
            OperaBundle(bundle_path, strict=strict)

    def test_load_success(self, tmp_path: pathlib.Path):
        bundle_path = tmp_path / "mini"
        csar_path: pathlib.Path = (_RESOURCE_DIRECTORY / "csar/mini/").resolve()
        OperaBundle.init(bundle_path, csar_path)
        OperaBundle(bundle_path, strict=True)

    def test_load_invalid_location(self):
        bundle_path = pathlib.Path("/does/not/exist")
        with pytest.raises(OperaBundleError):
            OperaBundle(bundle_path, strict=True)

    def test_load_partial_structure(self, tmp_path: pathlib.Path):
        (tmp_path / OperaBundle.SUBDIR_CSAR).mkdir()
        (tmp_path / OperaBundle.SUBDIR_TEMPLATES).mkdir()
        # missing instances

        with pytest.raises(OperaBundleError):
            OperaBundle(tmp_path, strict=True)
