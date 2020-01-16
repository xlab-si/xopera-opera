import json


def save(name, csar, inputs):
    # TODO(@tadeboro): Temporary placeholder
    with open("{}.deploy".format(name), "w") as fd:
        json.dump(dict(name=csar, inputs=inputs), fd)


def load(name):
    # TODO(@tadeboro): Temporary placeholder
    with open("{}.deploy".format(name)) as fd:
        data = json.load(fd)
    return data["name"], data["inputs"]
