from dataclasses import field

from scraper.graph.base_objects import NodeBase


class Movie(NodeBase):
    year: int = field(default=0)
    total_grossing: float = field(default=0)
