from dataclasses import dataclass, field

from scraper.graph.base_objects import EntityType, NodeBase
from scraper.graph.movie import Movie


@dataclass
class Actor(NodeBase):
    """
    Actor node
    """
    age: int = field(default=0)

    def __post_init__(self) -> None:
        super().__post_init__()
        self.type = EntityType.ACTOR

    @property
    def grossing(self) -> float:
        """
        Get the total grossing for the actor
        Returns:
            the grossing
        """
        total = 0.0
        for edge in self.get_edges():
            for node in edge.ends:
                if node != self and isinstance(node, Movie):
                    total += node.total_grossing * edge.weight
        return total

    def __eq__(self, other: object) -> bool:
        return super().__eq__(other)
