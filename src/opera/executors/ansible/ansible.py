import json
import os
import sys
import tempfile

import yaml

from opera.threading import utils as thread_utils
from . import utils
from .stdout_callbacks import json_ansible_callback


def _get_inventory(host):
    inventory = dict(
        ansible_host=host,
        ansible_ssh_common_args="-o StrictHostKeyChecking=no",
    )

    if host == "localhost":
        inventory["ansible_connection"] = "local"
        inventory["ansible_python_interpreter"] = sys.executable
    else:
        inventory["ansible_user"] = os.environ.get("OPERA_SSH_USER", "centos")
        opera_ssh_identity_file = os.environ.get("OPERA_SSH_IDENTITY_FILE")
        if opera_ssh_identity_file is not None:
            inventory["ansible_ssh_private_key_file"] = opera_ssh_identity_file

    return yaml.safe_dump(dict(all=dict(hosts=dict(opera=inventory))))


def run(host, primary, dependencies, artifacts, variables, verbose, workdir, validate):
    # pylint: disable=too-many-locals
    with tempfile.TemporaryDirectory() as dir_path:
        playbook = os.path.join(dir_path, os.path.basename(primary))
        utils.copy(os.path.join(workdir, primary), playbook)

        for d in dependencies:
            utils.copy(os.path.join(workdir, d), os.path.join(dir_path, os.path.basename(d)))
        for a in artifacts:
            utils.copy(os.path.join(workdir, a), os.path.join(dir_path, os.path.basename(a)))

        inventory = utils.write(dir_path, _get_inventory(host), suffix=".yaml")
        vars_file = utils.write(dir_path, yaml.safe_dump(variables), suffix=".yaml")

        with open(f"{dir_path}/ansible.cfg", "w", encoding="utf-8") as fd:
            fd.write("[defaults]\n")
            fd.write("retry_files_enabled = False\n")

            opera_ssh_host_key_checking = os.environ.get("OPERA_SSH_HOST_KEY_CHECKING")
            if opera_ssh_host_key_checking is not None:
                check = str(opera_ssh_host_key_checking).lower().strip()
                if check[:1] == "f" or check[:1] == "false":
                    fd.write("host_key_checking = False\n")

        if verbose:
            print(json.dumps({"inputs": {key: variables[key] for key in variables}}, indent=2, sort_keys=True))

        cmd = [
            "ansible-playbook",
            "-i", inventory,
            "-e", "@" + vars_file,
            playbook
        ]

        if validate:
            cmd.append("--syntax-check")

        env = dict(
            ANSIBLE_SHOW_CUSTOM_STATS="1",
            ANSIBLE_CALLBACK_PLUGINS=f"~/.ansible/plugins/callback:/usr/share/ansible/plugins/callback:"
                                     f"{os.path.dirname(json_ansible_callback.__file__)}",
            ANSIBLE_STDOUT_CALLBACK="json_ansible_callback"
        )
        code, out, err = utils.run_in_directory(dir_path, cmd, env)
        if code != 0 or verbose:
            with open(out, encoding="utf-8") as fd:
                thread_utils.SafePrinter.print_lines(fd)
            with open(err, encoding="utf-8") as fd:
                thread_utils.SafePrinter.print_lines(fd)
            thread_utils.print_thread("============")

        if code != 0:
            return False, {}

        outputs = {}
        if not validate:
            with open(out, encoding="utf-8") as fd:
                outputs = json.load(fd)["global_custom_stats"]
        return code == 0, outputs
