import os
import pathlib
import textwrap
import zipfile

import pytest

from opera.parser import yaml


@pytest.fixture
def yaml_text():
    def _yaml_text(string_data):
        return textwrap.dedent(string_data)

    return _yaml_text


@pytest.fixture
def yaml_ast():
    def _yaml_ast(string_data):
        return yaml.load(textwrap.dedent(string_data), "TEST")

    return _yaml_ast


# https://stackoverflow.com/questions/1855095/
@pytest.fixture
def zip_directory_contents():
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

    return _zip_directory_contents
