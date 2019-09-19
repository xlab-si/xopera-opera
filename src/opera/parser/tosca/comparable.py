from .base import Base


class Comparable(Base):
    def __eq__(self, other: "Comparable"):
        return self.data == other.data

    def __hash__(self):
        return hash(self.data)
