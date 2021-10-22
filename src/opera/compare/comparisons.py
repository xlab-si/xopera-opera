from .diff import Diff


class Comparison:
    def __init__(self, compare_func):
        self.item_compare_func = compare_func

    def compare(self, collection1, collection2, context):
        return self.item_compare_func(collection1, collection2, context)


class ListComparison(Comparison):
    def __init__(self, compare_func, id_func):
        super().__init__(compare_func)
        self.item_id_func = id_func

    def compare(self, collection1, collection2, context):  # pylint: disable=arguments-differ
        diff = Diff()
        for item1 in collection1:
            item2 = next((i for i in collection2 if self.item_id_func(item1) == self.item_id_func(i)), None)
            if not item2:
                diff.deleted.append(self.item_id_func(item1))
            else:
                equal, change = self.item_compare_func(item1, item2, context)
                if not equal:
                    diff.changed[self.item_id_func(item1)] = change
        for item2 in collection2:
            item1 = next((i for i in collection1 if self.item_id_func(item2) == self.item_id_func(i)), None)
            if not item1:
                diff.added.append(self.item_id_func(item2))

        return diff.equal(), diff


class MapComparison(Comparison):
    def __init__(self, compare_func, id_func=None):
        super().__init__(compare_func)
        self.item_id_func = id_func

    def compare(self, collection1, collection2, context):  # pylint: disable=arguments-differ
        if collection1 is None:
            collection1 = {}
        if collection2 is None:
            collection2 = {}

        # special handling for capability properties and attributes
        if isinstance(collection1, tuple):
            collection1 = collection1[0]
        if isinstance(collection2, tuple):
            collection2 = collection2[0]

        diff = Diff()
        for name1, item1 in collection1.items():
            if name1 not in collection2:
                diff.deleted.append(name1)
            else:
                equal, change = self.item_compare_func(item1, collection2[name1], context)
                if not equal:
                    if self.item_id_func is None:
                        name = name1
                    else:
                        name = self.item_id_func(item1)
                    diff.changed[name] = change

        for name2 in collection2:
            if name2 not in collection1:
                diff.added.append(name2)

        return diff.equal(), diff
