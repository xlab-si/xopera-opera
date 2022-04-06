from __future__ import (absolute_import, division, print_function)

import json

from ansible.inventory.host import Host
from ansible.parsing.ajson import AnsibleJSONEncoder
from ansible.plugins.callback import CallbackBase

__metaclass__ = type

DOCUMENTATION = '''
callback: json_ansible_callback
callback_type: stdout
requirements:
  - Set as stdout in config
short_description: Show Ansible output as JSON
version_added: "2.0"
description:
    - This callback converts Ansible playbook standard output to JSON
notes:
  - We had to create out custom JSON callback plugin for opera's Asnible executor because json callback is not present
    in ansible.builtin Ansible collection and is now part of ansible.posix Ansible collection, which is not included in
    ansible-core PyPI package, but only in ansible PyPI package.
'''


class CallbackModule(CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = "stdout"
    CALLBACK_NAME = "json_ansible_callback"

    def __init__(self):
        super().__init__()
        self.tasks = {}

    def dump_result(self, result):
        # pylint: disable=protected-access
        task_result = {"name": self.tasks[result._task._uuid], "result": result._result}
        self._display.display(json.dumps(task_result, cls=AnsibleJSONEncoder, indent=2, sort_keys=True))

    def v2_playbook_on_task_start(self, task, is_conditional):
        # pylint: disable=protected-access
        self.tasks[task._uuid] = task.name

    def v2_playbook_on_stats(self, stats):
        custom_stats = {k.get_name() if isinstance(k, (Host,)) else k: v for k, v in stats.custom.items()}

        output = {
            "stats": {h: stats.summarize(h) for h in stats.processed.keys()},
            "custom_stats": custom_stats,
            "global_custom_stats": custom_stats.pop("_run", {}),
        }

        self._display.display(json.dumps(output, cls=AnsibleJSONEncoder, indent=2, sort_keys=True))
