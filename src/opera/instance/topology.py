import collections


class Topology:
    def __init__(self, storage, nodes):
        self.storage = storage
        self.nodes = {n.tosca_id: n for n in nodes}

        for node in self.nodes.values():
            node.topology = self
            node.instantiate_relationships()
            node.read()

    def deploy(self):
        # TODO(@tadeboro): This is where parallelization magic should go.
        # Currently, we are running a really stupid O(n^3) algorithm, but
        # unless we get to the templates with millions of node instances, we
        # should be fine.

        do_deploy = True
        while do_deploy:
            do_deploy = False
            for node in self.nodes.values():
                if not node.deployed and node.ready_for_deploy:
                    node.deploy()
                    do_deploy = True

    def undeploy(self):
        # TODO(@tadeboro): This is where parallelization magic should go.
        # Currently, we are running a really stupid O(n^3) algorithm, but
        # unless we get to the templates with millions of node instances, we
        # should be fine.

        do_undeploy = True
        while do_undeploy:
            do_undeploy = False
            for node in self.nodes.values():
                if not node.undeployed and node.ready_for_undeploy:
                    node.undeploy()
                    do_undeploy = True

    def write(self, data, instance_id):
        self.storage.write_json(data, "instances", instance_id)

    def read(self, instance_id):
        return self.storage.read_json("instances", instance_id)
