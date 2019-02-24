from dataclasses import dataclass
from typing import Tuple

from scraper.graph.node_base import NodeBase


@dataclass
class Edge:
    edge_id: int
    weight: float
    ends: Tuple[NodeBase, NodeBase]

    def __contains__(self, node: NodeBase) -> bool:
        return node in self.ends
