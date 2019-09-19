from typing import Any, IO

from opera.parser.yaml.node import Node
from .loader import Loader


def load(stream: IO[Any], stream_path: str) -> Node:
    ldr = Loader(stream, stream_path)
    try:
        return ldr.get_single_data()
    finally:
        ldr.dispose()
