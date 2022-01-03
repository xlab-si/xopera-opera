from io import TextIOWrapper
from threading import current_thread, Lock  # type: ignore # pylint: disable=no-name-in-module


def print_thread(string):
    print(f"[{current_thread().name}] {string}")


class SafePrinter:
    lock = Lock()

    @classmethod
    def print_lines(cls, wrapper: TextIOWrapper):
        with cls.lock:
            print_thread("------------")
            for line in wrapper:
                print(line.rstrip())
