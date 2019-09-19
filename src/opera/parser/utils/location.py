class Location:
    def __init__(self, stream_name: str, line: int, column: int):
        self.stream_name = stream_name
        self.line = line
        self.column = column

    def __str__(self):
        return "{}:{}:{}".format(self.stream_name, self.line, self.column)
