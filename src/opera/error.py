import pathlib

from opera.parser.utils.location import Location


class OperaError(Exception):
    """ Base opera exception for catch-all-opera-errors constructs. """


class ParseError(OperaError):
    """ Exception that is raised on invalid TOSCA document. """

    def __init__(self, msg: str, loc: Location):
        super().__init__(msg)
        self.loc = loc


class CsarValidationError(OperaError):
    """ Raised when the CSAR does not conform to the TOSCA specification. """

    def __init__(self, msg: str, tosca_standard_section: str):
        # TODO: differentiate between standard versions?
        super().__init__("{} (TOSCA Simple Profile v1.3 section {})".format(msg, tosca_standard_section))
        self.tosca_standard_section = tosca_standard_section


class UnsupportedToscaFeatureError(OperaError):
    """ Raised when attempting to use a TOSCA feature that is not supported by xopera. """


class FileOutOfBoundsError(OperaError):
    """ Raised when attempting to access a file outside the bounds of a CSAR. """

    def __init__(self, base_path: pathlib.PurePath, relative_path: pathlib.PurePath):
        super().__init__("Error accessing {}, out of bounds of {}.".format(str(relative_path), str(base_path)))
