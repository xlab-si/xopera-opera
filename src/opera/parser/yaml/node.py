from typing import Optional

from opera.parser.utils.location import Location


class Node:
    def __init__(self, value, loc: Optional[Location] = None):
        self.value = value
        self.loc: Location = loc or Location("", 0, 0)

    def _dump_header(self):
        return "{}({})".format(type(self.value).__name__, self.loc)

    def _dump_map(self, pad: str):
        children = (
            "  {}{}: {}".format(pad, k.dump(pad + "  "), v.dump(pad + "  "))
            for k, v in self.value.items()
        )
        return "{head}{{\n{children}\n{pad}}}".format(
            head=self._dump_header(), children=",\n".join(children), pad=pad,
        )

    def _dump_seq(self, pad: str):
        children = (pad + "  " + v.dump(pad + "  ") for v in self.value)
        return "{head}[\n{children}\n{pad}]".format(
            head=self._dump_header(), children=",\n".join(children), pad=pad,
        )

    def dump(self, pad=""):
        if type(self.value) is list:
            return self._dump_seq(pad)
        if type(self.value) is dict:
            return self._dump_map(pad)
        # No padding for scalars, since the are inlined in the dump.
        return "{}({})".format(self._dump_header(), self.value)

    @property
    def bare(self):
        if type(self.value) is list:
            return [v.bare for v in self.value]
        if type(self.value) is dict:
            return {k.bare: v.bare for k, v in self.value.items()}
        return self.value

    def __str__(self):
        return self.dump()
