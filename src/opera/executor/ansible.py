import json
import os
import sys
import tempfile

import yaml

from . import utils
from opera.threading import utils as thread_utils


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


def run(host, primary, dependencies, vars):
    with tempfile.TemporaryDirectory() as dir_path:
        playbook = os.path.join(dir_path, os.path.basename(primary))
        utils.copy(primary, playbook)
        for d in dependencies:
            utils.copy(d, os.path.join(dir_path, os.path.basename(d)))
        inventory = utils.write(
            dir_path, _get_inventory(host), suffix=".yaml",
        )
        vars_file = utils.write(
            dir_path, yaml.safe_dump(vars), suffix=".yaml",
        )
        with open("{}/ansible.cfg".format(dir_path), "w") as fd:
            fd.write("[defaults]\n")
            fd.write("retry_files_enabled = False\n")

        cmd = [
            "ansible-playbook",
            "-i", inventory,
            "-e", "@" + vars_file,
            playbook
        ]
        env = dict(
            ANSIBLE_SHOW_CUSTOM_STATS="1",
            ANSIBLE_STDOUT_CALLBACK="json",
        )
        code, out, err = utils.run_in_directory(dir_path, cmd, env)
        if code != 0:
            thread_utils.print_thread("------------")
            with open(out) as fd:
                for l in fd:
                    print(l.rstrip())
            thread_utils.print_thread("------------")
            with open(err) as fd:
                for l in fd:
                    print(l.rstrip())
            thread_utils.print_thread("============")
            return False, {}

        with open(out) as fd:
            outputs = json.load(fd)["global_custom_stats"]
        return code == 0, outputs
