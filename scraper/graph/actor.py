from scraper.graph.node_base import NodeBase


class Actor(NodeBase):
    age: int
    grossing_cache: float = 0
