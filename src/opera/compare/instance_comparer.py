from typing import Dict

from opera.constants import NodeState
from .comparisons import MapComparison
from .diff import Diff


class InstanceComparer:
    def compare_topology_template(self, topology_template1, topology_template2, template_diff):
        diff_copy = template_diff.copy()
        nodes_diff = diff_copy.changed.get("nodes", Diff())
        # we can just process model from second topology
        # as we only care about the relationships that are present
        root_nodes2 = self._get_root_nodes(topology_template2.nodes)
        equal, diff = self._check_dependencies(root_nodes2.values(), nodes_diff.changed, None, False)
        if not equal:
            nodes_diff.combine_changes("dependencies", diff)
        compare_states = MapComparison(self._compare_state, self._get_template_name)
        equal, diff = compare_states.compare(topology_template1.nodes, topology_template2.nodes, None)
        if not equal:
            nodes_diff.combine_changes("state", diff.changed)

        return equal, diff_copy

    def prepare_update(self, topology_template1, topology_template2, template_diff):
        # no need to take relationships into account
        # as they are always in "initial" state
        nodes_diff = template_diff.changed.get("nodes", Diff())
        for node1 in topology_template1.nodes.values():
            node_name = self._get_template_name(node1)
            if not nodes_diff.find_key(node_name):
                node1.set_state(NodeState.INITIAL, write=False)

        for node2 in topology_template2.nodes.values():
            node_name = self._get_template_name(node2)
            if not nodes_diff.find_key(node_name):
                node2.set_state(NodeState.STARTED, write=False)

    def _check_dependencies(self, nodes, changed_nodes, parent_name, parent_changed):
        dependency_changes: Dict[str, set] = {}
        # dependency graph is acyclic so we may not care about
        # marking processed nodes
        for node in nodes:
            node_changed = node.template.name in changed_nodes
            for edge in node.in_edges.values():
                _, child_changes = self._check_dependencies(
                    map(self._get_source, edge.values()),
                    changed_nodes,
                    node.template.name,
                    node_changed
                )
                for child_name, changes in child_changes.items():
                    node_dep = dependency_changes.get(child_name, set())
                    node_dep.update(changes)
                    if child_name not in dependency_changes:
                        dependency_changes[child_name] = node_dep
            if parent_changed:
                node_name = self._get_template_name(node)
                node_dep = dependency_changes.get(node_name, set())
                node_dep.add(node_name)
                if node_name not in dependency_changes:
                    dependency_changes[node_name] = node_dep
        return len(dependency_changes) == 0, dependency_changes

    @staticmethod
    def _get_root_nodes(nodes):
        root_nodes = {}
        for node_name, node in nodes.items():
            if len(node.out_edges) == 0:
                root_nodes[node_name] = node
        return root_nodes

    @staticmethod
    def _get_template_name(node):
        return node.template.name

    @staticmethod
    def _get_source(relationship):
        return relationship.source

    @staticmethod
    def _compare_state(node1, node2, context):
        # comparing states we assume that all nodes in new instance model
        # would be in "started" state after deployment
        state1 = node1.state
        return state1 == NodeState.STARTED, [state1, NodeState.STARTED]
