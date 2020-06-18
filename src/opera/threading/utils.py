from threading import current_thread


def print_thread(str):
    print("[{}] {}".format(current_thread().name, str))
