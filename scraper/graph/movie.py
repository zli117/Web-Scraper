from scraper.graph.node_base import NodeBase


class Movie(NodeBase):
    year: int
    total_grossing: float
