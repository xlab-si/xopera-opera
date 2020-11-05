import shutil
import yaml

from pathlib import Path
from tempfile import TemporaryDirectory, mktemp
from zipfile import ZipFile

from opera.error import ParseError


class CloudServiceArchive:
    def __init__(self, csar_name):
        self._csar_name = csar_name
        self._tosca_meta = None
        self._root_yaml_template = None
        self._metadata = None

    def package_csar(self, output, service_template=None, csar_format="zip"):
        try:
            meta_file_path = Path(
                self._csar_name) / "TOSCA-Metadata" / "TOSCA.meta"

            if not service_template:
                root_yaml_files = []
                root_yaml_files.extend(Path(self._csar_name).glob('*.yaml'))
                root_yaml_files.extend(Path(self._csar_name).glob('*.yml'))

                if not meta_file_path.exists() and len(root_yaml_files) != 1:
                    raise ParseError(
                        "You didn't specify the CSAR TOSCA entrypoint with "
                        "'-t/--service-template' option. Therefore there "
                        "should be one YAML file in the root of the CSAR to "
                        "select it as the entrypoint. More than one YAML has "
                        "been found: {}. Please select one of the files as "
                        "the CSAR entrypoint using '-t/--service-template' "
                        "flag or remove all the excessive YAML files.".format(
                            list(map(str, root_yaml_files))), self)
                service_template = root_yaml_files[0].name
            else:
                if not Path(self._csar_name).joinpath(
                        service_template).exists():
                    raise ParseError('The supplied TOSCA service template '
                                     'file "{}" does not exist in folder '
                                     '"{}".'.format(service_template,
                                                    self._csar_name), self)

            if meta_file_path.exists():
                # check existing TOSCA.meta file
                with meta_file_path.open() as meta_file:
                    self._tosca_meta = yaml.safe_load(meta_file)

                self._validate_csar_version()
                self._validate_tosca_meta_file_version()

                template_entry = self._get_entry_definitions()
                if service_template and template_entry != service_template:
                    raise ParseError('The file entry "{}" defined within '
                                     '"Entry-Definitions" in '
                                     '"TOSCA-Metadata/TOSCA.meta" does not '
                                     'match with the file name "{}" supplied '
                                     'in service_template CLI argument.'.
                                     format(template_entry, service_template),
                                     self)

                # check if 'Entry-Definitions' points to an existing
                # template file in the CSAR
                if not Path(self._csar_name).joinpath(template_entry).exists():
                    raise ParseError('The file "{}" defined within '
                                     '"Entry-Definitions" in '
                                     '"TOSCA-Metadata/TOSCA.meta" does '
                                     'not exist.'.format(template_entry), self)
                return shutil.make_archive(output, csar_format,
                                           self._csar_name)
            else:
                # use tempdir because we don't want to modify user's folder
                # with TemporaryDirectory(prefix="opera-package-") as tempdir
                # cannot be used because shutil.copytree would fail due to the
                # existing temporary folder (this happens only when running
                # with python version lower than 3.8)
                tempdir = mktemp(prefix="opera-package-")
                # create tempdir and copy in all the needed CSAR files
                shutil.copytree(self._csar_name, tempdir)

                # create TOSCA-Metadata/TOSCA.meta file using the specified
                # TOSCA service template or directory root YAML file
                content = """
                          TOSCA-Meta-File-Version: 1.1
                          CSAR-Version: 1.1
                          Created-By: xOpera TOSCA orchestrator
                          Entry-Definitions: {}
                          """.format(service_template)

                meta_file_folder = Path(tempdir) / "TOSCA-Metadata"
                meta_file = (meta_file_folder / "TOSCA.meta")

                meta_file_folder.mkdir()
                meta_file.touch()
                meta_file.write_text(content)

                return shutil.make_archive(output, csar_format, tempdir)
        except Exception as e:
            raise ParseError("Error when creating CSAR: {}".format(e), self)

    def unpackage_csar(self, output_dir, csar_format="zip"):
        # unpack the CSAR to the specified location
        shutil.unpack_archive(self._csar_name, output_dir, csar_format)

    def validate_csar(self):
        with TemporaryDirectory() as tempdir:
            ZipFile(self._csar_name, 'r').extractall(tempdir)

            try:
                meta_file_path = Path(
                    tempdir) / "TOSCA-Metadata" / "TOSCA.meta"
                if meta_file_path.exists():
                    with meta_file_path.open() as meta_file:
                        self._tosca_meta = yaml.safe_load(meta_file)

                    self._validate_csar_version()
                    self._validate_tosca_meta_file_version()
                    template_entry = self._get_entry_definitions()

                    # check if 'Entry-Definitions' points to an existing
                    # template file in the CSAR
                    if not Path(tempdir).joinpath(template_entry).exists():
                        raise ParseError('The file "{}" defined within '
                                         '"Entry-Definitions" in '
                                         '"TOSCA-Metadata/TOSCA.meta" does '
                                         'not exist.'.format(template_entry),
                                         self)

                    return template_entry
                else:
                    root_yaml_files = []

                    root_yaml_files.extend(Path(tempdir).glob('*.yaml'))
                    root_yaml_files.extend(Path(tempdir).glob('*.yml'))

                    if len(root_yaml_files) != 1:
                        raise ParseError("There should be one root level YAML "
                                         "file in the root of the CSAR: {}."
                                         .format(root_yaml_files), self)

                    with Path(root_yaml_files[0]).open() as root_template:
                        root_yaml_template = yaml.safe_load(root_template)
                        self._metadata = root_yaml_template.get('metadata')

                    self._get_template_version()
                    self._get_template_name()

                    return root_yaml_files[0].name
            except Exception as e:
                raise ParseError("Invalid CSAR structure: {}".format(e), self)

    def _validate_csar_version(self):
        csar_version = self._tosca_meta.get('CSAR-Version')
        if csar_version and csar_version != 1.1:
            raise ParseError('CSAR-Version entry in the CSAR {} is '
                             'required to denote version 1.1".'.
                             format(self._csar_name), self)
        return csar_version

    def _validate_tosca_meta_file_version(self):
        tosca_meta_file_version = self._tosca_meta.get(
            'TOSCA-Meta-File-Version')
        if tosca_meta_file_version and tosca_meta_file_version != 1.1:
            raise ParseError(
                'TOSCA-Meta-File-Version entry in the CSAR {} is '
                'required to denote version 1.1".'.format(
                    self._csar_name), self)
        return tosca_meta_file_version

    def _get_entry_definitions(self):
        if 'Entry-Definitions' not in self._tosca_meta:
            raise ParseError(
                'The CSAR "{}" is missing the required metadata '
                '"Entry-Definitions" in "TOSCA-Metadata/TOSCA.meta".'.format(
                    self._csar_name), self)
        return self._tosca_meta.get('Entry-Definitions')

    # prepared for future, currently not used since this is an optional keyname
    def _get_created_by(self):
        return self._tosca_meta.get('Created-By')

    # prepared for future, currently not used since this is an optional keyname
    def _get_other_definitions(self):
        return self._tosca_meta.get('Other-Definitions')

    def _get_template_version(self):
        if "template_version" not in self._metadata:
            raise Exception(
                'The CSAR "{}" is missing the required '
                'template_version in metadata".'.format(self._csar_name))
        return self._metadata.get('template_version')

    def _get_template_name(self):
        if "template_version" not in self._metadata:
            raise ParseError(
                'The CSAR "{}" is missing the required '
                'template_name in metadata".'.format(self._csar_name), self)
        return self._metadata.get('template_name')

    # prepared for future, currently not used since this is an optional keyname
    def _get_author(self):
        return self._metadata.get('template_author')
