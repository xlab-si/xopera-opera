from .loader import Loader


def load(stream, stream_path):
    ldr = Loader(stream, stream_path)
    try:
        return ldr.get_single_data()
    finally:
        ldr.dispose()
