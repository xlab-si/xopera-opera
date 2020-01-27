class OperaError(Exception):
    """ Base opera exception for catch-all-opera-errors constructs. """


class ParseError(OperaError):
    """ Exception that is raised on invalid TOSCA document. """

    def __init__(self, msg, loc):
        super().__init__(msg)
        self.loc = loc


class DataError(OperaError):
    """ Exception that is raised on data errors that occur at runtime. """


class OperationError(OperaError):
    """ Raised on failed operation executions. """
