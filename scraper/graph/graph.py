from typing import Dict, List

from scraper.graph.edge import Edge
from scraper.graph.node_base import NodeBase, Url


class Graph:
    def __init__(self):
        self.nodes: List[NodeBase] = []
        self.edges: List[Edge] = []
        self.url_to_node: Dict[Url, NodeBase] = {}

    def check_node_exist(self, url: Url) -> bool:
        return url in self.url_to_node

    def add_node(self, node: NodeBase) -> bool:
        url = node.url
        if self.check_node_exist(url):
            return False
        node.node_id = len(self.nodes)
        self.nodes.append(node)
        self.url_to_node[url] = node
        return True

    def add_relationship(self, node_id_1: int, node_id_2: int) -> bool:
        if (0 <= node_id_1 < len(self.nodes)
                and 0 <= node_id_2 < len(self.nodes)):
            node_1 = self.nodes[node_id_1]
            node_2 = self.nodes[node_id_2]
            if node_1.has_peer(node_2):
                return False
            edge = Edge(edge_id=len(self.edges), ends=(node_1, node_2),
                        weight=0.0)
            node_1.add_edge(edge)
            node_2.add_edge(edge)
            return True
        return False

    def serialize(self) -> str:
        pass

    def deserialize(self, json: str) -> None:
        pass
