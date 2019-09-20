from pathlib import Path

import pytest
from opera.parser import tosca

_RESOURCE_DIRECTORY = Path(__file__).parent.parent.parent.parent.absolute() / "resources/"


class TestParser:
    @pytest.mark.parametrize("basepath,yamlpath", [(_RESOURCE_DIRECTORY, "mini.yaml")])
    def test_load_yaml(self, basepath, yamlpath):
        tosca.load(Path(basepath), yamlpath)
