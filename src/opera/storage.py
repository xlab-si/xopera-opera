import json
import pathlib
import shutil


class Storage:
    DEFAULT_INSTANCE_PATH = ".opera"

    @classmethod
    def create(cls, instance_path: str = None) -> "Storage":
        return Storage(pathlib.Path(instance_path or cls.DEFAULT_INSTANCE_PATH))

    def __init__(self, path):
        self.path = path.absolute()

        path.mkdir(exist_ok=True)

    def write(self, content, *path):
        *subpath, name = path
        dir_path = self.path / pathlib.PurePath(*subpath)
        dir_path.mkdir(exist_ok=True, parents=True)
        (dir_path / name).write_text(content)

    def read(self, *path):
        return (self.path / pathlib.PurePath(*path)).read_text()

    def write_json(self, data, *path):
        self.write(json.dumps(data, indent=2), *path)

    def read_json(self, *path):
        return json.loads(self.read(*path))

    def exists(self, *path):
        return (self.path / pathlib.PurePath(*path)).exists()

    def remove(self, *path):
        if self.exists(*path):
            shutil.rmtree(self.path / pathlib.PurePath(*path))

    def remove_all(self):
        shutil.rmtree(self.path)
        # the storage dir needs to exist after we delete the content
        pathlib.Path(self.path).mkdir(exist_ok=True)

