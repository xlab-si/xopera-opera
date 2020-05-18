import argparse
from pathlib import Path, PurePath
import shutil
import tempfile
from zipfile import ZipFile

from opera.error import DataError, ParseError
from opera.parser import tosca
from opera.storage import Storage


def add_parser(subparsers):
    parser = subparsers.add_parser(
        "package",
        help="Package service template and all accompanying files into a CSAR"
    )
    parser.add_argument(
        "--output", "-O", type=argparse.FileType("w"),
        help="Output file (the CSAR)",
    )
    parser.add_argument(
        "--library-source", "-L",
        help="Path to the library files")
    parser.add_argument("service_template",
                        type=argparse.FileType("r"),
                        help="Path to the root of the service template")
    parser.set_defaults(func=package)


def copy_libraries(dest_path, missing_imports, library_source):
    for imp in missing_imports:
        lib_candidate = library_source / imp.parent
        csar_prefix = imp.parent
        print(f"candidate: {lib_candidate} -> {dest_path / csar_prefix}")
        shutil.copytree(lib_candidate, dest_path / csar_prefix)


def copy_service(dest_path, service_path):
    print(f"Service: {service_path} -> {dest_path}")
    shutil.copytree(service_path, dest_path, symlinks=True)


def compress_service(source_path, output):
    with ZipFile(output.name, "w") as csar:
        for path in source_path.glob("**/*"):
            pathname = str(path)
            rel_pathname = str(path.relative_to(source_path))
            csar.write(pathname, arcname=rel_pathname)


def package(args):
    service_template_path = PurePath(args.service_template.name)
    service_path = service_template_path.parent
    library_path = PurePath(args.library_source)
    try:
        missing_imports = tosca.load_for_imports_list(Path.cwd(),
                                                      service_template_path)
    except ParseError as e:
        print("{}: {}".format(e.loc, e))
        return 1
    except DataError as e:
        print(str(e))
        return 1

    with tempfile.TemporaryDirectory(prefix="opera-") as tempdir:
        dest_path = Path(tempdir) / "service"
        copy_service(dest_path, service_path)
        copy_libraries(dest_path, missing_imports, library_path)
        compress_service(dest_path, args.output)

    return 0
