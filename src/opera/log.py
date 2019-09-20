import logging as base_logging
import os
import sys
from typing import Optional


def _get_level_from_envvar(default=base_logging.DEBUG) -> int:
    level_raw = os.getenv("LOG_LEVEL", None)
    if level_raw is None:
        return default

    level_raw = level_raw.strip().lower()
    string_levels = {
        "debug": base_logging.DEBUG,
        "info": base_logging.INFO,
        "warning": base_logging.WARNING,
        "warn": base_logging.WARNING,
        "error": base_logging.ERROR,
        "critical": base_logging.CRITICAL
    }
    return string_levels.get(level_raw, default)


def get_logger(module_name: Optional[str] = None) -> base_logging.Logger:
    """
    :param module_name: The logger module tag to use; if not specified, the logger uses the calling module's full name.
    """

    if module_name is None:
        import inspect
        stack = inspect.stack()
        if len(stack) < 2:
            # there is no parent frame, use this one
            frameinfo = stack[0]
        else:
            frameinfo = stack[1]
        module_name = frameinfo.frame.f_locals["__name__"]

    global_log_level = _get_level_from_envvar()

    result = base_logging.getLogger(module_name)
    result.setLevel(global_log_level)

    # if the global log level is debug, verbose debug messages get printed to stderr
    # higher log levels don't print the module names and times, only the message
    # duplicate messages are printed (one to stdout and one to stderr) when debug mode is active
    if global_log_level == base_logging.DEBUG:
        debug_handler = base_logging.StreamHandler(sys.stderr)
        debug_handler.setLevel(base_logging.DEBUG)
        debug_formatter = base_logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
        debug_handler.setFormatter(debug_formatter)
        result.addHandler(debug_handler)

    cli_handler = base_logging.StreamHandler(sys.stdout)
    cli_handler.setLevel(base_logging.INFO)
    cli_formatter = base_logging.Formatter("%(message)s")
    cli_handler.setFormatter(cli_formatter)
    result.addHandler(cli_handler)

    return result
