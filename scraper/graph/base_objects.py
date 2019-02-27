from dataclasses import dataclass, field
from typing import Any, Dict, List, NewType, Tuple, cast

from scraper.graph.entity_type import EntityType

Url = NewType('Url', str)


@dataclass
class Edge:
    """
    Edge
    """
    weight: float
    ends: Tuple['NodeBase', 'NodeBase']

    def __contains__(self, node: 'NodeBase') -> bool:
        return node in self.ends

    def to_dict(self) -> Dict[str, Any]:
        result = {'weight': self.weight,
                  'ends': tuple(map(lambda n: n.node_id, self.ends))}
        return result


@dataclass
class NodeBase:
    """
    The base of a node
    """
    node_id: int = field(default=0)
    name: str = field(default='')
    type: EntityType = field(default=EntityType.MOVIE)
    url: Url = field(default=cast(Url, ''))

    def __post_init__(self):
        self._connections_: List[Edge] = []

    def add_edge(self, edge: Edge) -> None:
        self._connections_.append(edge)

    def get_edges(self) -> Tuple[Edge, ...]:
        return tuple(self._connections_)

    def has_peer(self, node: 'NodeBase') -> bool:
        for edge in self._connections_:
            if node in edge:
                return True
        return False

    def to_dict(self) -> Dict[str, Any]:
        result = {'class_name': self.__class__.__name__,
                  'module_name': self.__class__.__module__}
        for attr in self.__dict__:
            if not attr.endswith('_'):
                result[attr] = self.__dict__[attr]
        return result

    def from_dict(self, dct: Dict[str, Any]) -> bool:
        for attr, value in dct.items():
            if hasattr(self, attr) and not attr.endswith('_'):
                setattr(self, attr, value)
            else:
                return False
        return True

    def __eq__(self, other: object) -> bool:
        return isinstance(other, NodeBase) and self.node_id == other.node_id
