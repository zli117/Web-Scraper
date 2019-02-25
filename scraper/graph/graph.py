import importlib
import json
from typing import Any, Dict, List, Optional

from scraper.graph.base_objects import Edge, NodeBase, Url


class Graph:
    def __init__(self):
        self.nodes: List[NodeBase] = []
        self.edges: List[Edge] = []
        self.url_to_node: Dict[Url, NodeBase] = {}

    def check_node_exist(self, url: Url) -> bool:
        return url in self.url_to_node

    def add_node(self, node: NodeBase, set_id: bool = True) -> bool:
        url = node.url
        if self.check_node_exist(url):
            return False
        if set_id:
            node.node_id = len(self.nodes)
        self.nodes.append(node)
        self.url_to_node[url] = node
        return True

    def add_relationship(self, node_id_1: int,
                         node_id_2: int, set_id: bool = True) -> Optional[Edge]:
        if (0 <= node_id_1 < len(self.nodes)
                and 0 <= node_id_2 < len(self.nodes)):
            node_1 = self.nodes[node_id_1]
            node_2 = self.nodes[node_id_2]
            if not node_1.has_peer(node_2):
                edge = Edge(ends=(node_1, node_2),weight=0.0)
                node_1.add_edge(edge)
                node_2.add_edge(edge)
                self.edges.append(edge)
                return edge
        return None

    def serialize(self) -> str:
        serialized_nodes = list(map(lambda node: node.to_dict(), self.nodes))
        serialized_edges = list(map(lambda edge: edge.to_dict(), self.edges))
        return json.dumps(
            {'nodes': serialized_nodes, 'edges': serialized_edges})

    def deserialize(self, json_str: str) -> bool:
        json_dict = json.loads(json_str)
        serialized_nodes: List[Dict[str, Any]] = json_dict['nodes']
        serialized_edges: List[Dict[str, Any]] = json_dict['edges']

        # Deserialize nodes
        for node_dict in serialized_nodes:
            cls_name = node_dict.pop('class_name')
            cls = getattr(importlib.import_module('scraper.graph'), cls_name)
            node: NodeBase = cls()
            if not node.from_dict(node_dict):
                return False
            self.add_node(node, set_id=False)

        self.nodes.sort(key=lambda n: n.node_id)

        if self.nodes and self.nodes[-1].node_id != len(self.nodes) - 1:
            return False

        # Deserialize edge
        for edge_dict in serialized_edges:
            ends = edge_dict['ends']
            edge = self.add_relationship(*ends)
            if edge is None:
                return False
            edge.weight = edge_dict.get('weight', default=0)
