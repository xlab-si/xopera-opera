import argparse
import shtab

from pathlib import Path, PurePath

from opera.error import DataError, ParseError
from opera.parser.tosca.csar import CloudServiceArchive
from opera.utils import determine_archive_format, generate_random_pathname


def add_parser(subparsers):
    parser = subparsers.add_parser(
        "unpackage",
        help="Unpackage TOSCA CSAR to a specified location"
    )
    parser.add_argument(
        "--destination", "-d",
        help="Path to the location where the CSAR file will be extracted to, "
             "the path will be generated in the current working directory if "
             "it isn't specified",
    ).complete = shtab.DIR
    parser.add_argument(
        "--verbose", "-v", action='store_true',
        help="Turns on verbose mode",
    )
    parser.add_argument(
        "csar", help="Path to the compressed TOSCA CSAR"
    ).complete = shtab.FILE
    parser.set_defaults(func=_parser_callback)


def _parser_callback(args):
    csar_path = Path(args.csar)
    if not csar_path.is_file():
        raise argparse.ArgumentTypeError("CSAR file {} is not a valid path!"
                                         .format(args.csar))

    # if the output is set use it, if not create a random file name with UUID
    if args.destination:
        extracted_folder = Path(args.destination)
    else:
        # generate a unique extracted CSAR folder name
        extracted_folder = Path(generate_random_pathname("opera-unpackage-"))

    try:
        abs_csar_path = str(csar_path.resolve())
        abs_dest_path = str(extracted_folder.resolve())

        archive_format = determine_archive_format(abs_csar_path)
        unpackage(abs_csar_path, abs_dest_path, archive_format)
        print("The CSAR was unpackaged to '{}'.".format(abs_dest_path))
    except ParseError as e:
        print("{}: {}".format(e.loc, e))
        return 1
    except DataError as e:
        print(str(e))
        return 1

    return 0


def unpackage(csar_input: str, output_dir: str, csar_format: str):
    """
    :raises ParseError:
    :raises DataError:
    """
    csar = CloudServiceArchive.create(PurePath(csar_input))
    # validate CSAR before unpacking it
    csar.validate_csar()
    # unpack the CSAR to the specified location
    csar.unpackage_csar(output_dir)
