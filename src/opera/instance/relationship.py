from opera.error import DataError

from .base import Base


class Relationship(Base):
    def __init__(self, template, instance_id, source, target):
        super().__init__(template, instance_id)

        self.source = source
        self.target = target
