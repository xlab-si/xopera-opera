import pytest

from opera.cli import create_parser


class TestArgparse:
    def test_subparsers(self, service_template):
        parser = create_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["deploy", "-h"])
            parser.parse_args(["diff", "-h"])
            parser.parse_args(["info", "-h"])
            parser.parse_args(["notify", "-h"])
            parser.parse_args(["outputs", "-h"])
            parser.parse_args(["package", "-h"])
            parser.parse_args(["undeploy", "-h"])
            parser.parse_args(["unpackage", "-h"])
            parser.parse_args(["update", "-h"])
            parser.parse_args(["validate", "-h"])
