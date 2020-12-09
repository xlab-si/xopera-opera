import pathlib

import pytest

from opera.error import ParseError
from opera.parser.tosca.path import Path
from opera.parser.yaml.node import Node


class TestBuild:
    def test_build(self):
        assert isinstance(Path.build(Node("/")).data, pathlib.PurePath)


class TestPrefixPath:
    @pytest.mark.parametrize("input,prefix", [
        ("/a/b", "c"), ("/a", "b"), ("/a", "../.."), ("/c", "."),
    ])
    def test_prefix_absolute_path(self, input, prefix):
        path = Path(pathlib.PurePath(input), None)
        path.prefix_path(pathlib.PurePath(prefix))

        assert str(path.data) == input

    @pytest.mark.parametrize("input,prefix,output", [
        ("a", "b", "b/a"),
        ("a", "..", "../a"),
        ("a", ".", "a"),
        ("a/b", "c", "c/a/b"),
        ("a/b", "..", "../a/b"),
        ("a/b", "c/d", "c/d/a/b"),
        ("a", "c/d/", "c/d/a"),
    ])
    def test_prefix_relative_path(self, input, prefix, output):
        path = Path(pathlib.PurePath(input), None)
        path.prefix_path(pathlib.PurePath(prefix))

        assert str(path.data) == output


class TestResolvePath:
    def test_valid_dir_path(self, tmp_path):
        rel_path = pathlib.PurePath("some/folder")
        abs_path = tmp_path / rel_path
        abs_path.mkdir(parents=True)

        path = Path(rel_path, None)
        path.resolve_path(tmp_path)

        assert rel_path == path.data

    def test_valid_file_path(self, tmp_path):
        rel_path = pathlib.PurePath("some/file.txt")
        abs_path = tmp_path / rel_path
        abs_path.parent.mkdir(parents=True)
        abs_path.write_text("sample_text")

        path = Path(rel_path, None)
        path.resolve_path(tmp_path)

        assert rel_path == path.data

    def test_valid_rel_path_with_dots(self, tmp_path):
        rel_path = pathlib.PurePath("a/././b/../c/../d")
        abs_path = (tmp_path / rel_path).resolve()
        abs_path.mkdir(parents=True)

        path = Path(rel_path, None)
        path.resolve_path(tmp_path)

        assert pathlib.PurePath("a/d") == path.data

    def test_valid_abs_path_with_dots(self, tmp_path):
        rel_path = pathlib.PurePath("e/./f/g/h/../i/..")
        abs_path = (tmp_path / rel_path).resolve()
        abs_path.mkdir(parents=True)

        path = Path("/" / rel_path, None)
        path.resolve_path(tmp_path)

        assert pathlib.PurePath("e/f/g") == path.data

    def test_missing_file(self, tmp_path):
        with pytest.raises(ParseError):
            Path(pathlib.PurePath("missing"), None).resolve_path(tmp_path)

    def test_symlink(self, tmp_path):
        file = tmp_path / "file.txt"
        file.write_text("file")
        symlink = tmp_path / "symlink"
        symlink.symlink_to(file)

        with pytest.raises(ParseError):
            Path(pathlib.PurePath("symlink"), None).resolve_path(tmp_path)

    @pytest.mark.parametrize("path", [
        "..", "../a", "../../a/b", "a/../..", "a/b/../c/../../..",
        "/..", "/../a", "/../../a/b", "/a/../..", "/a/b/../c/../../..",
    ])
    def test_escape_csar(self, tmp_path, path):
        with pytest.raises(ParseError):
            Path(pathlib.PurePath(path), None).resolve_path(tmp_path)

    def test_csar_root(self, tmp_path):
        with pytest.raises(ParseError):
            Path(pathlib.PurePath("/c/.."), None).resolve_path(tmp_path)
