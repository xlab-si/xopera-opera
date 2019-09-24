from abc import abstractclassmethod
from pathlib import Path, PurePath
from typing import TypeVar, Generic

from opera.parser.yaml import Node

TDocument = TypeVar("TDocument")


class ToscaParser(Generic[TDocument]):
    """A base class for parsing TOSCA documents, subclasses for different TOSCA editions and document types."""

    @abstractclassmethod
    def parse(cls, yaml_node: Node, base_path: Path, csar_path: PurePath) -> TDocument:
        pass
