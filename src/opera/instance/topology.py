from typing import Optional

from opera.threading import NodeExecutor


class Topology:
    def __init__(self, storage, nodes):
        self.storage = storage
        self.nodes = {n.tosca_id: n for n in nodes}

        for node in self.nodes.values():
            node.topology = self
            node.instantiate_relationships()
            node.read()

    def status(self):
        if any(node.deploying for node in self.nodes.values()):
            return "deploying"

        if all(node.deployed for node in self.nodes.values()):
            return "deployed"

        if any(node.undeploying for node in self.nodes.values()):
            return "undeploying"

        if all(node.undeployed for node in self.nodes.values()):
            return "undeployed"

        if any(node.error for node in self.nodes.values()):
            return "error"

        return "unknown"

    def validate(self, verbose, workdir, num_workers=None):
        # Currently, we are running a really stupid O(n^3) algorithm, but unless we get to the templates with
        # millions of node instances, we should be fine.
        with NodeExecutor(num_workers) as executor:
            do_validate = True
            while do_validate:
                for node in self.nodes.values():
                    if not node.validated and executor.can_submit(node.tosca_id):
                        executor.submit_operation(node.validate, node.tosca_id, verbose, workdir)
                do_validate = executor.wait_results()

    def deploy(self, verbose, workdir, num_workers=None):
        # Currently, we are running a really stupid O(n^3) algorithm, but unless we get to the templates with
        # millions of node instances, we should be fine.
        with NodeExecutor(num_workers) as executor:
            do_deploy = True
            while do_deploy:
                for node in self.nodes.values():
                    if (not node.deployed
                            and node.ready_for_deploy
                            and executor.can_submit(node.tosca_id)):
                        executor.submit_operation(node.deploy, node.tosca_id, verbose, workdir)
                do_deploy = executor.wait_results()

    def undeploy(self, verbose, workdir, num_workers=None):
        # Currently, we are running a really stupid O(n^3) algorithm, but unless we get to the templates with
        # millions of node instances, we should be fine.
        with NodeExecutor(num_workers) as executor:
            do_undeploy = True
            while do_undeploy:
                for node in self.nodes.values():
                    if (not node.undeployed
                            and node.ready_for_undeploy
                            and executor.can_submit(node.tosca_id)):
                        executor.submit_operation(node.undeploy, node.tosca_id, verbose, workdir)
                do_undeploy = executor.wait_results()

    def notify(self, verbose: bool, workdir: str, trigger_name_or_event: Optional[str],
               notification_file_contents: Optional[str], num_workers=1):
        # This will run selected interface operations on triggers from policies that have been applied to nodes.
        with NodeExecutor(num_workers) as executor:
            do_notify = True
            while do_notify:
                for node in self.nodes.values():
                    if not node.notified and executor.can_submit(node.tosca_id):
                        executor.submit_operation(node.notify, node.tosca_id, verbose, workdir, trigger_name_or_event,
                                                  notification_file_contents)
                do_notify = executor.wait_results()

    def write(self, data, instance_id):
        self.storage.write_json(data, "instances", instance_id)

    def write_all(self):
        for node in self.nodes.values():
            node.write()

    def read(self, instance_id):
        return self.storage.read_json("instances", instance_id)

    def set_storage(self, storage):
        self.storage = storage
