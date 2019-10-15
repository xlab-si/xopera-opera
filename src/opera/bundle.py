import pathlib
import zipfile

from opera.csar import ToscaCsar
from opera.error import OperaBundleError


class OperaBundle:
    """A grouping of xOpera files stored in a .opera/ directory."""

    DIRECTORY_NAME = ".opera"
    SUBDIR_CSAR = "csar"
    SUBDIR_TEMPLATES = "templates"
    SUBDIR_INSTANCES = "instances"

    def __init__(self, path: pathlib.Path, strict):
        """Create a reference to a bundle on disk.

        :param path: The bundle's base path, i.e. the .opera/ directory.
        :param strict: Whether to strictly validate the bundle and load the CSAR,
                       see OperaBundle::validate and ToscaCsar::validate.
        """

        self.base_path = path
        if strict:
            self.validate()
        self.csar = ToscaCsar.load(str((self.base_path / OperaBundle.SUBDIR_CSAR).resolve()), strict=strict)

    @staticmethod
    def init(base_path: pathlib.Path, csar_path: pathlib.Path) -> "OperaBundle":
        """Initialise a new xOpera bundle with a CSAR.

        Raises an error if the path already exists.
        """
        if base_path.exists():
            raise OperaBundleError("Base xOpera bundle path {} already exists.".format(base_path)) \
                from FileExistsError()

        if not csar_path.exists():
            raise OperaBundleError("CSAR at {} does not exist.".format(csar_path)) from IOError()

        base_path = base_path.resolve()
        csar_path = csar_path.resolve()

        print("Creating bare directory structure.")
        base_path.mkdir()
        (base_path / OperaBundle.SUBDIR_TEMPLATES).mkdir()
        (base_path / OperaBundle.SUBDIR_INSTANCES).mkdir()

        bundle_csar_path = base_path / OperaBundle.SUBDIR_CSAR
        if csar_path.is_dir():
            print("Processing a directory CSAR, linking {} to {}.".format(csar_path, bundle_csar_path))
            bundle_csar_path.symlink_to(csar_path, target_is_directory=True)
        else:
            print("Processing a zipped CSAR, unzipping {} to {}.".format(csar_path, bundle_csar_path))
            bundle_csar_path.mkdir()
            try:
                with zipfile.ZipFile(csar_path) as zf:
                    zf.extractall(path=bundle_csar_path)
            except zipfile.BadZipFile as e:
                raise OperaBundleError("CSAR files must be zip files.") from e

        # don't strictly load because the CSAR might be invalid,
        # and we don't care about that for initialisation
        return OperaBundle(base_path, strict=False)

    def validate(self):
        csar_path = (self.base_path / OperaBundle.SUBDIR_CSAR).resolve()
        templates_path = (self.base_path / OperaBundle.SUBDIR_TEMPLATES).resolve()
        instances_path = (self.base_path / OperaBundle.SUBDIR_INSTANCES).resolve()

        for path, what in [
            (self.base_path, "path"),
            (csar_path, "CSAR path"),
            (templates_path, "templates path"),
            (instances_path, "instances path")
        ]:
            if not path.exists():
                raise OperaBundleError("The bundle {} does not exist.".format(what))
            if not path.is_dir():
                raise OperaBundleError("The bundle {} is not a directory.".format(what))
