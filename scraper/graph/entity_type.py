from enum import Enum


class EntityType(Enum):
    MOVIE = 1
    ACTOR = 2

    def __str__(self):
        return self.name
