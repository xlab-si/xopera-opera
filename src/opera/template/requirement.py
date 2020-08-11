class Requirement:
    def __init__(self, name, target_name, relationship, occurrences=None):
        self.name = name
        self.target_name = target_name
        self.target = None
        self.relationship = relationship
        self.occurrences = occurrences

    def resolve(self, topology):
        self.target = topology.get_node(self.target_name)
        self.relationship.topology = topology
