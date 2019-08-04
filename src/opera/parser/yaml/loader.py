from .constructor import Constructor
from .resolver import Resolver


try:
    from _yaml import CParser

    class Loader(CParser, Constructor, Resolver):
        def __init__(self, stream, stream_name):
            CParser.__init__(self, stream)
            Constructor.__init__(self, stream_name)
            Resolver.__init__(self)


except ImportError:
    from yaml.composer import Composer
    from yaml.parser import Parser
    from yaml.reader import Reader
    from yaml.scanner import Scanner

    class Loader(Reader, Scanner, Parser, Composer, Constructor, Resolver):
        def __init__(self, stream, stream_name):
            Reader.__init__(self, stream)
            Scanner.__init__(self)
            Parser.__init__(self)
            Composer.__init__(self)
            Constructor.__init__(self, stream_name)
            Resolver.__init__(self)
