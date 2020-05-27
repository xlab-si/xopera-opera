from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

import yaml
from opera.error import ParseError


class CloudServiceArchive:
    def __init__(self, csar_name, csar_folder_path):
        self._csar_name = csar_name
        self._csar_folder_path = csar_folder_path
        self._tosca_meta = None
        self._root_yaml_template = None
        self._metadata = None

    def validate_csar(self):
        with TemporaryDirectory(dir=self._csar_folder_path) as tempdir:
            ZipFile(self._csar_name, 'r').extractall(tempdir)

            try:
                meta_file_path = Path(tempdir) / "TOSCA-Metadata" / "TOSCA.meta"
                if meta_file_path.exists():
                    with meta_file_path.open() as meta_file:
                        self._tosca_meta = yaml.safe_load(meta_file)

                    self._validate_csar_version()
                    self._validate_tosca_meta_file_version()
                    template_entry = self._get_entry_definitions()
                    self._get_created_by()
                    self._get_other_definitions()

                    # check if 'Entry-Definitions' points to an existing template file in the CSAR
                    if not Path(tempdir).joinpath(template_entry).exists():
                        raise ParseError('The file "{}" defined within "Entry-Definitions" in '
                                         '"TOSCA-Metadata/TOSCA.meta" does not exist.'.format(template_entry), self)

                    return template_entry
                else:
                    root_yaml_files = []

                    root_yaml_files.extend(Path(tempdir).glob('*.yaml'))
                    root_yaml_files.extend(Path(tempdir).glob('*.yml'))

                    if len(root_yaml_files) != 1:
                        raise ParseError("There should be one root level yaml "
                                         "file in the root of the CSAR: {}.".format(root_yaml_files), self)

                    with Path(root_yaml_files[0]).open() as root_template:
                        root_yaml_template = yaml.safe_load(root_template)
                        self._metadata = root_yaml_template.get('metadata')

                    self._get_template_version()
                    self._get_template_name()
                    self._get_author()

                    return root_yaml_files[0].name
            except Exception as e:
                raise ParseError("Invalid CSAR structure: {}".format(e), self)

    def _validate_csar_version(self):
        csar_version = self._tosca_meta.get('CSAR-Version')
        if csar_version and csar_version != 1.1:
            raise ParseError('CSAR-Version entry in the CSAR {} is '
                             'required to denote version 1.1".'.format(self._csar_name), self)
        return csar_version

    def _validate_tosca_meta_file_version(self):
        tosca_meta_file_version = self._tosca_meta.get('TOSCA-Meta-File-Version')
        if tosca_meta_file_version and tosca_meta_file_version != 1.1:
            raise ParseError('TOSCA-Meta-File-Version entry in the CSAR {} is '
                             'required to denote version 1.1".'.format(self._csar_name), self)
        return tosca_meta_file_version

    def _get_entry_definitions(self):
        if 'Entry-Definitions' not in self._tosca_meta:
            raise ParseError('The CSAR "{}" is missing the required metadata "Entry-Definitions" in '
                             '"TOSCA-Metadata/TOSCA.meta".'.format(self._csar_name), self)
        return self._tosca_meta.get('Entry-Definitions')

    def _get_created_by(self):
        return self._tosca_meta.get('Created-By')

    def _get_other_definitions(self):
        return self._tosca_meta.get('Other-Definitions')

    def _get_template_version(self):
        if "template_version" not in self._metadata:
            raise Exception('The CSAR "{}" is missing the required '
                            'template_version in metadata".'.format(self._csar_name))
        return self._metadata.get('template_version')

    def _get_template_name(self):
        if "template_version" not in self._metadata:
            raise ParseError('The CSAR "{}" is missing the required'
                             ' template_name in metadata".'.format(self._csar_name), self)
        return self._metadata.get('template_name')

    def _get_author(self):
        return self._metadata.get('template_author')
