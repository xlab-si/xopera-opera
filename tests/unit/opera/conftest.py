import textwrap

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
