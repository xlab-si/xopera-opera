import yaml
import json

from zipfile import is_zipfile
from tarfile import is_tarfile
from uuid import uuid4
from os import path
from pathlib import Path, PurePath

from opera.parser import tosca


def prompt_yes_no_question(yes_responses=("y", "yes"),
                           no_responses=("n", "no"),
                           case_sensitive=False,
                           default_yes_response=True):

    prompt_message = "Do you want to continue? (Y/n): "
    if not default_yes_response:
        prompt_message = "Do you want to continue? (y/N): "

    check = str(input(prompt_message)).strip()
    if not case_sensitive:
        check = check.lower()

    try:
        if check == "":
            return default_yes_response
        if check in yes_responses:
            return True
        elif check in no_responses:
            return False
        else:
            print("Invalid input. Please try again.")
            return prompt_yes_no_question(yes_responses, no_responses,
                                          case_sensitive, default_yes_response)
    except Exception as e:
        print("Exception occurred: {}. Please enter valid inputs.".format(e))
        return prompt_yes_no_question(yes_responses, no_responses,
                                      case_sensitive, default_yes_response)


def determine_archive_format(filepath):
    if is_tarfile(filepath):
        return "tar"
    elif is_zipfile(filepath):
        return "zip"
    else:
        raise Exception("Unsupported archive format: '{}'. The packaging "
                        "format should be one of: zip, tar.".format(filepath))


def generate_random_pathname(prefix=""):
    # use uuid4 to create a unique random pathname and select last 6 characters
    pathname = prefix + str(uuid4().hex)[-6:]
    if path.exists(pathname):
        return generate_random_pathname(prefix)
    else:
        return pathname


def format_outputs(outputs, format):
    if format == "json":
        return json.dumps(outputs, indent=2)
    if format == "yaml":
        return yaml.safe_dump(outputs, default_flow_style=False)

    assert False, "BUG - invalid format"


def save_outputs(outputs, format, filename):
    with open(filename, 'w+') as outfile:
        if format == "json":
            return json.dumps(outputs, outfile, indent=2)
        if format == "yaml":
            return yaml.safe_dump(outputs, outfile, default_flow_style=False)

        assert False, "BUG - invalid format"


def get_workdir(storage):
    if storage.exists("csars"):
        csar_dir = Path(storage.path) / "csars" / "csar"
        return str(csar_dir)
    else:
        return str(Path.cwd())


def get_template(storage):
    if storage.exists("inputs"):
        inputs = storage.read_json("inputs")
    else:
        inputs = {}

    if storage.exists("root_file"):
        service_template = storage.read("root_file")

        if storage.exists("csars"):
            csar_dir = Path(storage.path) / "csars" / "csar"
            ast = tosca.load(Path(csar_dir),
                             PurePath(service_template).relative_to(csar_dir))
        else:
            ast = tosca.load(Path.cwd(), PurePath(service_template))

        template = ast.get_template(inputs)
        return template
    else:
        return None
