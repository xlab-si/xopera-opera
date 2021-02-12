class Trigger:
    def __init__(self, name, event, target_filter, condition, action):
        self.name = name
        self.event = event
        self.target_filter = target_filter
        self.condition = condition
        self.action = action

    # this will link trigger's target filter to targeted node object
    def resolve_event_filter(self, nodes):
        if self.target_filter:
            resolved = False
            for node_name, node in nodes.items():
                if node_name == self.target_filter[0] or node.types[0] == self.target_filter[0]:
                    self.target_filter = node_name, node
                    resolved = True
                    break

            # if we haven't found targeted node object (this can happen for example when node type is defined but is
            # not used in anywhere in topology within node_templates section) then unset target_filter
            if not resolved:
                self.target_filter = None
