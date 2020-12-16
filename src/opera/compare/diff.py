class Diff:
    def __init__(self):
        self.added = []
        self.changed = {}
        self.deleted = []

    def equal(self):
        return (len(self.added) == 0 and
                len(self.changed) == 0 and
                len(self.deleted) == 0)

    def outputs(self, level):
        return self.convert(self, level)

    def convert(self, diff, level):
        if not isinstance(diff, Diff):
            return diff
        contents = {}
        if len(diff.added) != 0:
            contents["added"] = diff.added
        if len(diff.deleted) != 0:
            contents["deleted"] = diff.deleted
        if len(diff.changed) != 0:
            changed = {}
            for key, val in diff.changed.items():
                changed[key] = self.convert(val, level - 1)
            if len(contents) == 0:
                contents = changed
            else:
                contents["changed"] = changed
        return contents
