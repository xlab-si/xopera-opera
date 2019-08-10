import re

from .string import String


# TOSCA definition: <major>.<minor>[.<fix>[.<qualifier>[-<build]]]
#   major: is a required integer value greater than or equal to 0 (zero)
#   minor: is a required integer value greater than or equal to 0 (zero).
#   fix: is an optional integer value greater than or equal to 0 (zero).
#   qualifier: is an optional string that indicates a named, pre-release
#              version of the associated code that has been derived from the
#              version of the code identified by the combination
#              major_version, minor_version and fix_version numbers.
#   build: is an optional integer value greater than or equal to 0 (zero) that
#          can be used to further qualify different build versions of the code
#          that has the same qualifer_string.
VERSION_RE = re.compile(
    r"""
    ^
      (?P<major>[0-9]|([1-9][0-9]+))
    \.(?P<minor>[0-9]|([1-9][0-9]+))
    (
        \.(?P<fix>[0-9]|([1-9][0-9]+))
        (
            \.(?P<qualifier>\w+)
            (
                -(?P<build>[0-9]|([1-9][0-9]+))
            )?
        )?
    )?
    $
    """,
    re.ASCII | re.VERBOSE,
)


class Version(String):
    @classmethod
    def validate(cls, yaml_node):
        super().validate(yaml_node)
        if not VERSION_RE.match(yaml_node.value):
            cls.abort("Invalid version format.", yaml_node.loc)
