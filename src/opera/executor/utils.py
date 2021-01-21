import errno
import os
import shutil
import subprocess  # nosec
import tempfile


def copy(source, target):
    try:
        shutil.copytree(source, target)
    except OSError as e:
        if e.errno == errno.ENOTDIR:
            shutil.copy(source, target)
        else:
            raise


def write(dest_dir, content, suffix=None):
    dest = tempfile.NamedTemporaryFile(dir=dest_dir, delete=False, suffix=suffix)
    dest.write(content.encode("utf-8"))
    dest.close()
    return dest.name


def run_in_directory(dest_dir, cmd, env):
    fstdout = tempfile.NamedTemporaryFile(dir=dest_dir, delete=False, suffix=".stdout")
    fstderr = tempfile.NamedTemporaryFile(dir=dest_dir, delete=False, suffix=".stderr")
    result = subprocess.run(cmd, cwd=dest_dir, stdout=fstdout, stderr=fstderr,  # nosec
                            env=dict(os.environ, **env), check=False)
    fstdout.close()
    fstderr.close()
    return result.returncode, fstdout.name, fstderr.name
