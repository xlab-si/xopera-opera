from .loader import Loader


def load(stream, stream_path):
    loader = Loader(stream, stream_path)
    try:
        return loader.get_single_data()
    finally:
        loader.dispose()
