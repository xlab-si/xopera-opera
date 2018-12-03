from __future__ import print_function, unicode_literals

import yaml


def run(playbook):
    print("Running ansible {}".format(playbook))
    return dict(id="abc123", xx=123)
    # make temporary folder
    # copy playbook there
    # copy artifacts
    # set proper variables
    # run ansible
    # parse attributes
