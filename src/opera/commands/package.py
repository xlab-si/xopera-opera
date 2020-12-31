import argparse
import shtab

from pathlib import Path, PurePath

from opera.error import DataError, ParseError
from opera.parser.tosca.csar import CloudServiceArchive
from opera.utils import generate_random_pathname


def add_parser(subparsers):
    parser = subparsers.add_parser(
        "package",
        help="Package service template and all accompanying files into a CSAR"
    )
    parser.add_argument(
        "--service-template", "-t",
        help="Name or path to the TOSCA service template "
             "file from the root of the input folder",
    )
    parser.add_argument(
        "--output", "-o",
        help="Output CSAR file path",
    )
    parser.add_argument(
        "--format", "-f", choices=("zip", "tar"),
        default="zip", help="CSAR compressed file format",
    )
    parser.add_argument(
        "--verbose", "-v", action='store_true',
        help="Turns on verbose mode",
    )
    parser.add_argument(
        "service_template_folder",
        help="Path to the root of the service template or "
             "folder you want to create the TOSCA CSAR from"
    ).complete = shtab.FILE
    parser.set_defaults(func=_parser_callback)


def _parser_callback(args):
    if not Path(args.service_template_folder).is_dir():
        raise argparse.ArgumentTypeError("Directory {} is not a valid path!"
                                         .format(args.service_template_folder))

    # if the output is set use it, if not create a random file name with UUID
    if args.output:
        # remove file extension if needed (".zip" or ".tar")
        # because shutil.make_archive already adds the extension
        if args.output.endswith("." + args.format):
            csar_output = str(Path(args.output).with_suffix(''))
        else:
            csar_output = str(Path(args.output))

    else:
        # generate a create a unique random file name
        csar_output = generate_random_pathname("opera-package-")

    try:
        output_package = package(args.service_template_folder, csar_output,
                                 args.service_template, args.format)
        print("CSAR was created and packed to '{}'.".format(output_package))
    except ParseError as e:
        print("{}: {}".format(e.loc, e))
        return 1
    except DataError as e:
        print(str(e))
        return 1

    return 0


def package(input_dir: str, csar_output: str, service_template: str,
            csar_format: str) -> str:
    """
    :raises ParseError:
    :raises DataError:
    """
    csar = CloudServiceArchive.create(PurePath(input_dir))
    return csar.package_csar(csar_output, service_template, csar_format)
