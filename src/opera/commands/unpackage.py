import argparse
from pathlib import Path, PurePath

import shtab
from opera_tosca_parser.parser import tosca

from opera.error import DataError, ParseError
from opera.utils import generate_random_pathname


def add_parser(subparsers):
    parser = subparsers.add_parser(
        "unpackage",
        help="Unpackage TOSCA CSAR (zip file) to a specified location"
    )
    parser.add_argument(
        "--destination", "-d",
        help="Path to the location where the CSAR file will be extracted to, the path will be generated in the "
             "current working directory if it isn't specified",
    ).complete = shtab.DIR
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Turns on verbose mode",
    )
    parser.add_argument(
        "csar",
        help="Path to the TOSCA CSAR (zip file)"
    ).complete = shtab.FILE
    parser.set_defaults(func=_parser_callback)


def _parser_callback(args):
    csar_path = Path(args.csar)
    if not csar_path.is_file():
        raise argparse.ArgumentTypeError(f"CSAR file {args.csar} is not a valid path!")

    # if the output is set use it, if not create a random file name with UUID
    if args.destination:
        extracted_folder = Path(args.destination)
    else:
        # generate a unique extracted CSAR folder name
        extracted_folder = Path(generate_random_pathname("opera-unpackage-"))

    try:
        abs_csar_path = PurePath(csar_path.resolve())
        abs_dest_path = PurePath(extracted_folder.resolve())

        unpackage(abs_csar_path, abs_dest_path)
        print(f"The CSAR was unpackaged to '{abs_dest_path}'.")
    except ParseError as e:
        print(f"{e.loc}: {e}")
        return 1
    except DataError as e:
        print(str(e))
        return 1

    return 0


def unpackage(csar_input: PurePath, output_dir: PurePath):
    csar = tosca.load_csar(csar_input)
    # unpack the CSAR to the specified location
    csar.unpackage_csar(output_dir)
