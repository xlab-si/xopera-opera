class OperaError(Exception):
    """Base opera exception for catch-all-opera-errors constructs."""


class ParseError(OperaError):
    """Exception that is raised on invalid TOSCA document."""

    def __init__(self, msg, loc):
        super().__init__(msg)
        self.loc = loc


class DataError(OperaError):
    """Exception that is raised on data errors that occur at runtime."""


class OperationError(OperaError):
    """Raised on failed operation executions."""

    def __init__(self, msg, tosca_name, interface, operation):
        super().__init__(f"{msg} in {tosca_name}, interface {interface}, operation {operation}.")
        self.tosca_name = tosca_name
        self.interface = interface
        self.operation = operation


class ToscaDeviationError(OperaError):
    """Raised when something is compatible with TOSCA standard, but not acceptable for the orchestrator."""


class AggregatedOperationError(OperaError):
    def __init__(self, msg, inner_exceptions):
        super().__init__(msg)
        self.inner_exceptions = inner_exceptions
