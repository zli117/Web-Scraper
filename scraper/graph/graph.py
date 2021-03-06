import importlib
import json
from typing import Any, Dict, List, Optional, Tuple

from scraper.graph.base_objects import Edge, EntityType, NodeBase, Url


class Graph:
    """
    The Graph structure
    """

    def __init__(self):
        self._nodes: List[NodeBase] = []
        self._edges: List[Edge] = []
        self._url_to_node: Dict[Url, NodeBase] = {}

    def num_node(self, node_type: EntityType) -> int:
        """
        Count number of node of a type
        Args:
            node_type: The type of the node

        Returns:
            The count
        """
        return sum(
            map(lambda node: 1 if node.type == node_type else 0, self._nodes))

    @property
    def nodes(self) -> Tuple[NodeBase, ...]:
        """
        Get all of the nodes
        Returns:
            A tuple of all the nodes
        """
        return tuple(self._nodes)

    @property
    def edges(self) -> Tuple[Edge, ...]:
        """
        Get all the eges
        Returns:
            A tuple of all the edges
        """
        return tuple(self._edges)

    def check_node_exist(self, url: Url) -> bool:
        """
        Check whether a node is already there
        Args:
            url: The url of the node

        Returns:
            True or false
        """
        return url in self._url_to_node

    def add_node(self, node: NodeBase, set_id: bool = True) -> bool:
        """
        Add a node to the graph. True if successful, false otherwise.
        """
        url = node.url
        if self.check_node_exist(url):
            return False
        if set_id:
            node.node_id = len(self._nodes)
        self._nodes.append(node)
        self._url_to_node[url] = node
        return True

    def add_relationship(self, node_id_1: int,
                         node_id_2: int) -> Optional[Edge]:
        """
        Add a relationship between nodes
        Args:
            node_id_1: Node 1
            node_id_2: Node 2

        Returns:
            True if successful false otherwise.
        """
        if (0 <= node_id_1 < len(self._nodes)
                and 0 <= node_id_2 < len(self._nodes)):
            node_1 = self._nodes[node_id_1]
            node_2 = self._nodes[node_id_2]
            if not node_1.has_peer(node_2):
                edge = Edge(ends=(node_1, node_2), weight=0.0)
                node_1.add_edge(edge)
                node_2.add_edge(edge)
                self._edges.append(edge)
                return edge
        return None

    def query_nodes(self, constraints: Dict[str, Any]) -> List[NodeBase]:
        """
        Query nodes with constraints
        Args:
            constraints: A dictionary of constraints

        Returns:
            A list of found node
        """
        result = []
        for node in self._nodes:
            for attr, value in constraints.items():
                if not hasattr(node, attr) or getattr(node, attr) != value:
                    break
            else:
                result.append(node)
        return result

    def serialize(self) -> str:
        """
        Serialize the graph
        Returns:
            Json string
        """
        serialized_nodes = list(map(lambda node: node.to_dict(), self._nodes))
        # serialized_nodes = [node.to_dict() for node in self._nodes]
        serialized_edges = list(map(lambda edge: edge.to_dict(), self._edges))
        # serialized_edges = [edge.to_dict() for edge in self._edges]
        return json.dumps(
            {'nodes': serialized_nodes, 'edges': serialized_edges})

    def deserialize(self, json_str: str) -> bool:
        """
        Construct from json
        Args:
            json_str:

        Returns:

        """
        json_dict = json.loads(json_str)
        serialized_nodes: List[Dict[str, Any]] = json_dict['nodes']
        serialized_edges: List[Dict[str, Any]] = json_dict['edges']

        # Deserialize nodes
        for node_dict in serialized_nodes:
            cls_name = node_dict.pop('class_name')
            module_name = node_dict.pop('module_name')
            cls = getattr(importlib.import_module(module_name), cls_name)
            node: NodeBase = cls()
            if not node.from_dict(node_dict):
                return False
            self.add_node(node, set_id=False)

        self._nodes.sort(key=lambda n: n.node_id)

        if self._nodes and self._nodes[-1].node_id != len(self._nodes) - 1:
            return False

        # Deserialize edge
        for edge_dict in serialized_edges:
            ends = edge_dict['ends']
            edge = self.add_relationship(*ends)
            if edge is None:
                return False
            edge.weight = edge_dict.get('weight', 0)

        return True
