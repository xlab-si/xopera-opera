from threading import current_thread  # type: ignore # pylint: disable=no-name-in-module


def print_thread(string):
    print(f"[{current_thread().name}] {string}")
