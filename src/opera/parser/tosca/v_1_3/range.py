import math

from ..base import Base


# NOTE: We do some pretty horrible checks in the validate function. There are
# two reasons for this mess:
#
#  1. TOSCA's range type is a bit ugly to parse because upper bound can be
#     string (UNBOUNDED) and should be treated as infinity.
#  2. Python's bool type subclasses int, which makes isinstance(False, int)
#     truthy. Thsi is why we have separate checks for bool.

class Range(Base):
    @classmethod
    def validate(cls, yaml_node):
        if not isinstance(yaml_node.value, list) or len(yaml_node.value) != 2:
            cls.abort("Expected two element list.", yaml_node.loc)

        low, high = yaml_node.value
        if not isinstance(low.value, int) or isinstance(low.value, bool):
            cls.abort("Lower bound must be integer.", low.loc)

        if isinstance(high.value, str) and high.value != "UNBOUNDED":
            cls.abort("Upper bound must be integer or UNBOUNDED.", high.loc)

        if not isinstance(high.value, (str, int)) or isinstance(high.value, bool):
            cls.abort("Upper bound must be integer or UNBOUNDED.", high.loc)

        if isinstance(high.value, int) and low.value > high.value:
            cls.abort(
                "Upper bound must be greater or equal to lower bound.",
                yaml_node.loc,
            )

    @classmethod
    def build(cls, yaml_node):
        low, high = yaml_node.value
        return cls(
            (low.value, math.inf if high.value == "UNBOUNDED" else high.value),
            yaml_node.loc,
        )
