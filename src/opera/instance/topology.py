from opera.threading import NodeExecutor


class Topology:
    def __init__(self, storage, nodes):
        self.storage = storage
        self.nodes = {n.tosca_id: n for n in nodes}

        for node in self.nodes.values():
            node.topology = self
            node.instantiate_relationships()
            node.read()

    def deploy(self, num_workers=None):
        # Currently, we are running a really stupid O(n^3) algorithm, but
        # unless we get to the templates with millions of node instances, we
        # should be fine.
        with NodeExecutor(num_workers) as executor:
            do_deploy = True
            while do_deploy:
                for node in self.nodes.values():
                    if (not node.deployed
                            and node.ready_for_deploy
                            and executor.not_submitted(node.tosca_id)):
                        executor.submit_operation(node.deploy, node.tosca_id)
                do_deploy = executor.wait_results()

    def undeploy(self, num_workers=None):
        # Currently, we are running a really stupid O(n^3) algorithm, but
        # unless we get to the templates with millions of node instances, we
        # should be fine.
        with NodeExecutor(num_workers) as executor:
            do_undeploy = True
            while do_undeploy:
                for node in self.nodes.values():
                    if (not node.undeployed
                            and node.ready_for_undeploy
                            and executor.not_submitted(node.tosca_id)):
                        executor.submit_operation(node.undeploy, node.tosca_id)
                do_undeploy = executor.wait_results()

    def write(self, data, instance_id):
        self.storage.write_json(data, "instances", instance_id)

    def read(self, instance_id):
        return self.storage.read_json("instances", instance_id)
