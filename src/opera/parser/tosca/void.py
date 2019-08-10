from opera.parser.yaml.node import Node

from .base import Base


class Void(Base):
    """
    Marker for parts of the document that should be parsed after initial
    semantic analysis.
    """

    @property
    def bare(self):
        return Node(self.data, self.loc).bare
