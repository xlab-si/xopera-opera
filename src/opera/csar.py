import json


def save(name, csar):
    # TODO(@tadeboro): Temporary placeholder
    with open("{}.deploy".format(name), "w") as fd:
        json.dump(dict(name=csar), fd)


def load(name):
    # TODO(@tadeboro): Temporary placeholder
    with open("{}.deploy".format(name)) as fd:
        return json.load(fd)["name"]
