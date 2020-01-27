import json
import os
import sys
import tempfile

import yaml

from . import utils


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
            with open(out) as fd:
                for l in fd:
                    print(l.rstrip())
            print("------------")
            with open(err) as fd:
                for l in fd:
                    print(l.rstrip())
            print("============")
            return False, {}

        with open(out) as fd:
            attributes = json.load(fd)["global_custom_stats"]
        return code == 0, attributes
