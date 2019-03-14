import json
import os
import shutil
import subprocess
import sys
import tempfile

import yaml


def _save_artifact_into(dest_dir, artifact, suffix=None):
    dest = tempfile.NamedTemporaryFile(
        dir=dest_dir, delete=False, suffix=suffix,
    )
    with open(artifact, "rb") as src:
        shutil.copyfileobj(src, dest)
    dest.close()
    return dest.name


def _save_content_into(dest_dir, content, suffix=None):
    dest = tempfile.NamedTemporaryFile(
        dir=dest_dir, delete=False, suffix=suffix,
    )
    dest.write(content.encode("utf-8"))
    dest.close()
    return dest.name


def _run_in(dest_dir, cmd, env):
    fstdout = tempfile.NamedTemporaryFile(
        dir=dest_dir, delete=False, suffix=".stdout",
    )
    fstderr = tempfile.NamedTemporaryFile(
        dir=dest_dir, delete=False, suffix=".stderr",
    )
    result = subprocess.run(
        cmd, cwd=dest_dir, stdout=fstdout, stderr=fstderr,
        env=dict(os.environ, **env),
    )
    fstdout.close()
    fstderr.close()
    return result.returncode, fstdout.name, fstderr.name


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


def run(host, playbook, vars):
    with tempfile.TemporaryDirectory() as dir_path:
        playbook = _save_artifact_into(dir_path, playbook, suffix=".yaml")
        inventory = _save_content_into(dir_path, _get_inventory(host))
        vars_file = _save_content_into(
            dir_path, yaml.safe_dump(vars), suffix=".yaml",
        )

        with open("{}/ansible.cfg".format(dir_path), "w") as fd:
            fd.write("[defaults]\n")
            fd.write("retry_files_enabled = False\n")

        # copy secondary artifacts
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
        code, out, err = _run_in(dir_path, cmd, env)
        if code != 0:
            with open(out) as fd:
                for l in fd:
                    print(l.rstrip())
            print("------------")
            with open(err) as fd:
                for l in fd:
                    print(l.rstrip())
            print("============")
        with open(out) as fd:
            attributes = json.load(fd)["global_custom_stats"]
        # TODO(@tadeboro): Do something sensible on error
        return code == 0, attributes
