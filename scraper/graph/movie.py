from dataclasses import dataclass, field

from scraper.graph.base_objects import EntityType, NodeBase


@dataclass
class Movie(NodeBase):
    year: int = field(default=0)
    total_grossing: float = field(default=0)

    def __post_init__(self):
        super().__post_init__()
        self.type = EntityType.MOVIE

    def __eq__(self, other) -> bool:
        return super().__eq__(other)
