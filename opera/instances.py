from __future__ import print_function, unicode_literals

import collections
import json

from opera import ansible


def get_type_hierarchy(typ):
    parents = []
    while typ:
        parents.append(typ.target)
        typ = typ.target.get("derived_from")
    return list(reversed(parents))


def merge_definitions(types):
    fields = dict(
        artifacts=collections.OrderedDict(),
        attributes=collections.OrderedDict(),
        capabilities=collections.OrderedDict(),
        interfaces=collections.OrderedDict(),
        properties=collections.OrderedDict(),
        requirements=collections.OrderedDict(),
    )
    for f in fields:
        for t in types:
            fields[f].update(t.get(f, {}))
    return fields


def instantiate_properties(template, definitions):
    prop_defs = definitions["properties"]
    result = {k: {"type": v["type"]} for k, v in prop_defs.items()}
    for k, v in prop_defs.items():
        if "default" in v:
            result[k]["value"] = v["default"]
    for k, v in template.get("properties", {}).items():
        if k in result:
            result[k]["value"] = v
    return result


def instantiate_attributes(template, definitions):
    attr_defs = definitions["attributes"]
    result = {k: {"type": v["type"]} for k, v in attr_defs.items()}
    for k, v in attr_defs.items():
        if "default" in v:
            result[k]["value"] = v["default"]
    return result


def instantiate_interfaces(template, definitions):
    # TODO(@tadeboro): Stop ignoring template overrides
    return {k: instantiate_interface(k, v)
            for k, v in definitions["interfaces"].items()}


def instantiate_interface(name, iface_def):
    # TODO(@tadeboro): Handle operation inputs
    result = {}
    for k, v in iface_def.items():
        if k == "type":
            continue
        result[k] = iface_def[k]
    return result


def instantiate_definitions(template, definitions):
    return dict(
        properties=instantiate_properties(template, definitions),
        attributes=instantiate_attributes(template, definitions),
        interfaces=instantiate_interfaces(template, definitions),
    )


def get_template_fields(template):
    definitions = merge_definitions(get_type_hierarchy(template["type"]))
    return instantiate_definitions(template, definitions)


class Instance(collections.OrderedDict):
    @classmethod
    def from_template(cls, name, template, inputs):
        # TODO(@tadeboro): Add template overrides and assignments
        fields = get_template_fields(template)
        fields["attributes"]["tosca_name"]["value"] = name
        fields["attributes"]["tosca_id"]["value"] = name + "0"
        return cls(fields)

    def dig(self, *args):
        item = self
        for a in args:
            item = item.get(a)
            if item is None:
                return None
        return item

    def save(self):
        data = {}
        for k, v in self["attributes"].items():
            if "value" in v:
                # TODO(@tadeboro): str conversion needs to go when we are done
                data[k] = str(v["value"])

        path = "{}.data".format(self["attributes"]["tosca_id"]["value"])
        with open(path, "w") as fd:
            json.dump(data, fd, indent=2, separators=(',', ': '))

    def load(self):
        path = "{}.data".format(self["attributes"]["tosca_id"]["value"])
        with open(path, "r") as fd:
            data = json.load(fd)
        for k, v in data.items():
            # TODO(@tadeboro): Add parsing here - currently we only support
            # string attributes
            self["attributes"][k]["value"] = v


class NodeInstance(Instance):
    DEPLOY_STEPS = ("create", "configure", "start")
    UNDEPLOY_STEPS = ("stop", "delete")

    def deploy(self):
        for s in self.DEPLOY_STEPS:
            playbook = self.dig(
                "interfaces", "Standard", s, "implementation", "primary"
            )
            if playbook is None:
                continue
            attributes = ansible.run(playbook)
            for k, v in attributes.items():
                if k in self["attributes"]:
                    self["attributes"][k]["value"] = v
            self.save()
