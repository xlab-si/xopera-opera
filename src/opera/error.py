from opera.parser.utils.location import Location


class OperaError(Exception):
    """ Base opera exception for catch-all-opera-errors constructs. """


class ParseError(OperaError):
    """ Exception that is raised on invalid TOSCA document. """

    def __init__(self, msg: str, loc: Location):
        super().__init__(msg)
        self.loc = loc
