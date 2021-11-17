import json
from os import path
from pathlib import Path, PurePath
from tarfile import is_tarfile
from uuid import uuid4
from zipfile import is_zipfile

import yaml

from opera.parser import tosca


def prompt_yes_no_question(
        yes_responses=("y", "yes"),
        no_responses=("n", "no"),
        case_sensitive=False,
        default_yes_response=True
):
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
            return prompt_yes_no_question(yes_responses, no_responses, case_sensitive, default_yes_response)
    except EOFError as e:
        print(f"Exception occurred: {e}. Please enter valid inputs.")
        return prompt_yes_no_question(yes_responses, no_responses, case_sensitive, default_yes_response)


def determine_archive_format(filepath):
    if is_tarfile(filepath):
        return "tar"
    elif is_zipfile(filepath):
        return "zip"
    else:
        raise Exception(
            f"Unsupported archive format: '{filepath}'. The packaging format should be one of: zip, tar."
        )


def generate_random_pathname(prefix=""):
    # use uuid4 to create a unique random pathname and select last 6 characters
    pathname = prefix + str(uuid4().hex)[-6:]
    if path.exists(pathname):
        return generate_random_pathname(prefix)
    else:
        return pathname


def format_outputs(outputs, outputs_format):
    if outputs_format == "json":
        return json.dumps(outputs, indent=2)
    if outputs_format == "yaml":
        return yaml.safe_dump(outputs, default_flow_style=False, sort_keys=False)

    raise AssertionError("BUG - invalid format")


def save_outputs(outputs, outputs_format, filename):
    with open(filename, "w+", encoding="utf-8") as outfile:
        if outputs_format == "json":
            return json.dump(outputs, outfile, indent=2)
        if outputs_format == "yaml":
            return yaml.safe_dump(outputs, outfile, default_flow_style=False, sort_keys=False)

        raise AssertionError("BUG - invalid format")


def get_workdir(storage):
    if storage.exists("csars"):
        csar_dir = Path(storage.path) / "csars" / "csar"
        return str(csar_dir)
    else:
        service_template_path = PurePath(storage.read("root_file"))
        return str(Path(service_template_path.parent))


def get_template(storage, workdir):
    if storage.exists("inputs"):
        inputs = storage.read_json("inputs")
    else:
        inputs = {}

    if storage.exists("root_file"):
        service_template_path = PurePath(storage.read("root_file"))

        if storage.exists("csars"):
            csar_dir = Path(storage.path) / "csars" / "csar"
            ast = tosca.load(Path(csar_dir), service_template_path.relative_to(csar_dir))
        else:
            ast = tosca.load(Path(workdir), PurePath(service_template_path.name))

        template = ast.get_template(inputs)
        return template
    else:
        return None
