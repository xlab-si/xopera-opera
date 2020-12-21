from .diff import Diff


class Comparison:
    def __init__(self, compare_func):
        self.item_compare_func = compare_func

    def compare(self, item1, item2, context):
        return self.item_compare_func(item1, item2, context)


class ListComparison(Comparison):
    def __init__(self, compare_func, id_func):
        super().__init__(compare_func)
        self.item_id_func = id_func

    def compare(self, list1, list2, context):
        diff = Diff()
        for item1 in list1:
            item2 = next((i for i in list2 if (self.item_id_func(item1) ==
                                               self.item_id_func(i))), None)
            if not item2:
                diff.deleted.append(self.item_id_func(item1))
            else:
                equal, change = self.item_compare_func(item1, item2, context)
                if not equal:
                    diff.changed[self.item_id_func(item1)] = change
        for item2 in list2:
            item1 = next((i for i in list1 if (self.item_id_func(item2) ==
                                               self.item_id_func(i))), None)
            if not item1:
                diff.added.append(self.item_id_func(item2))

        return diff.equal(), diff


class MapComparison(Comparison):
    def __init__(self, compare_func, id_func=None):
        super().__init__(compare_func)
        self.item_id_func = id_func

    def compare(self, dict1, dict2, context):
        if dict1 is None:
            dict1 = {}
        if dict2 is None:
            dict2 = {}
        # special handling for capability properties and attributes
        if isinstance(dict1, tuple):
            dict1 = dict1[0]
        if isinstance(dict2, tuple):
            dict2 = dict2[0]

        diff = Diff()
        for name1, item1 in dict1.items():
            if name1 not in dict2:
                diff.deleted.append(name1)
            else:
                equal, change = self.item_compare_func(item1,
                                                       dict2[name1],
                                                       context)
                if not equal:
                    if self.item_id_func is None:
                        name = name1
                    else:
                        name = self.item_id_func(item1)
                    diff.changed[name] = change

        for name2, item2 in dict2.items():
            if name2 not in dict1:
                diff.added.append(name2)

        return diff.equal(), diff
