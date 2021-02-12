class Policy:
    def __init__(self, name, types, properties, targets, triggers):
        self.types = types
        self.name = name
        self.properties = properties
        self.targets = targets
        self.triggers = triggers

    # this will link targets to their corresponding node objects
    def resolve_targets(self, nodes):
        if self.targets:
            for target_name in self.targets.copy().keys():
                resolved = False
                for node_name, node in nodes.items():
                    if node_name == target_name:
                        # just assign node object when target name is the same as the name of node object/template
                        self.targets[node_name] = node
                        resolved = True
                    elif node.types[0] == target_name:
                        # when target name matches node object's type we have to remove node type's key and replace it
                        # with the name of node object/template and then we assign node object to this new key
                        self.targets.pop(target_name, None)
                        self.targets[node_name] = node
                        resolved = True

                # if we haven't found targeted node object (this can happen for example when node type is defined
                # but is not used in anywhere in topology within node_templates section) then remove this target
                if not resolved:
                    self.targets.pop(target_name, None)
