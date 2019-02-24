from dataclasses import dataclass
from typing import List, NewType, Tuple

from scraper.graph.edge import Edge
from scraper.graph.entity_type import EntityType

Url = NewType('Url', str)


@dataclass
class NodeBase:
    node_id: int
    name: str
    type: EntityType
    url: Url
    _connections: List[Edge]

    def add_edge(self, edge: Edge) -> None:
        self._connections.append(edge)

    def get_edges(self) -> Tuple[Edge, ...]:
        return tuple(self._connections)

    def has_peer(self, node: 'NodeBase') -> bool:
        for edge in self._connections:
            if node in edge:
                return True
        return False

    def __eq__(self, other: 'NodeBase') -> bool:
        return self.node_id == other.node_id
