from dataclasses import field

from scraper.graph.base_objects import NodeBase


class Actor(NodeBase):
    age: int = field(default=0)
    grossing_cache: float = field(default=0)
