import math

from ..base import Base


# NOTE: We do some pretty horrible checks in the validate function. There are
# two reasons for this mess:
#
#  1. TOSCA's range type is a bit ugly to parse because upper bound can be
#     string (UNBOUNDED) and should be treated as infinity.
#  2. Python's bool type subclasses int, which makes isinstance(False, int)
#     trusty. This is why we have separate checks for bool.

class Range(Base):
    @classmethod
    def validate(cls, yaml_node):
        if not isinstance(yaml_node.value, list) or len(yaml_node.value) != 2:
            cls.abort("Expected two element list.", yaml_node.loc)

        lo, hi = yaml_node.value
        if not isinstance(lo.value, int) or isinstance(lo.value, bool):
            cls.abort("Lower bound must be integer.", lo.loc)

        if isinstance(hi.value, str) and hi.value != "UNBOUNDED":
            cls.abort("Upper bound must be integer or UNBOUNDED.", hi.loc)

        if not isinstance(hi.value, (str, int)) or isinstance(hi.value, bool):
            cls.abort("Upper bound must be integer or UNBOUNDED.", hi.loc)

        if isinstance(hi.value, int) and lo.value > hi.value:
            cls.abort(
                "Upper bound must be greater or equal to lower bound.",
                yaml_node.loc,
            )

    @classmethod
    def build(cls, yaml_node):
        lo, hi = yaml_node.value
        return cls(
            (lo.value, math.inf if hi.value == "UNBOUNDED" else hi.value),
            yaml_node.loc,
        )
