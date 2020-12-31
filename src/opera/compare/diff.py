import copy


class Diff:
    def __init__(self):
        self.added = []
        self.changed = {}
        self.deleted = []

    def equal(self):
        return (len(self.added) == 0 and
                len(self.changed) == 0 and
                len(self.deleted) == 0)

    def outputs(self):
        return self.convert(self)

    def convert(self, diff):
        if isinstance(diff, set):
            return list(diff)
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
                changed[key] = self.convert(val)
            if len(contents) == 0:
                contents = changed
            else:
                contents["changed"] = changed
        return contents

    def copy(self):
        return copy.deepcopy(self)

    def combine_changes(self, change_name, changes):
        for name, change in changes.items():
            if name not in self.changed:
                self.changed[name] = Diff()
            self.changed[name].changed[change_name] = change

    def find_key(self, key):
        return key in self.added or key in self.changed or key in self.deleted
