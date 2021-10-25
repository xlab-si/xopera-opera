from opera.parser.utils.location import Location


class Node:
    def __init__(self, value, loc=None):
        self.value = value
        self.loc = loc or Location("", 0, 0)

    @property
    def bare(self):
        if isinstance(self.value, list):
            return [v.bare for v in self.value]
        if isinstance(self.value, dict):
            return {k.bare: v.bare for k, v in self.value.items()}
        return self.value

    def __str__(self):
        return f"Node({self.loc})[{self.bare}]"
