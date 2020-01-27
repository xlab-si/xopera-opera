class Requirement:
    def __init__(self, name, target_name, relationship):
        self.name = name
        self.target_name = target_name
        self.target = None
        self.relationship = relationship

    def resolve(self, topology):
        self.target = topology.get_node(self.target_name)
