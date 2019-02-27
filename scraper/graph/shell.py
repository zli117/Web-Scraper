from typing import List, Optional, cast

from scraper.graph.actor import Actor
from scraper.graph.base_objects import EntityType
from scraper.graph.graph import Graph
from scraper.graph.movie import Movie


class ShellRunner:

    def __init__(self, graph: Graph) -> None:
        self.graph = graph
        self.terminated = False
        # TODO: Refactor this with meta class and decorator
        self.commands = {'end': 0,
                         'help': 0,
                         'list_nodes': 1,
                         'find_movie_gross': 1,
                         'find_movies_actor_worked_in': 1,
                         'list_actors_in_movie': 1,
                         'top_actor_grossing_value': 1,
                         'oldest_actors': 1,
                         'get_movie_of_year': 1,
                         'get_actor_of_year': 1}

    def start(self) -> None:
        self.terminated = False
        while not self.terminated:
            command = input('\033[94m### \033[0m').strip() + ' '
            func = command[:command.find(' ')]
            args = list(filter(lambda s: len(s) > 0,
                               map(lambda s: s.strip(),
                                   command[command.find(' '):].split(','))))
            print(func)
            print(args)
            if func in self.commands and len(args) == self.commands[func]:
                getattr(self, func)(*args)
            else:
                print('Invalid command name or number of arguments')

    def end(self) -> None:
        self.terminated = True

    def help(self) -> None:
        for name, nargs in self.commands.items():
            print('%s, num args: %d' % (name, nargs))

    def list_nodes(self, node_type: str) -> None:
        try:
            entity_type = EntityType[node_type]
            nodes = self.graph.query_nodes({'type': entity_type})
            for node in nodes:
                print(node.name)
        except KeyError:
            print('Invalid node type: %s' % node_type)

    def _find_movie(self, name: str) -> Optional[Movie]:
        movie = self.graph.query_nodes({'type': EntityType.MOVIE, 'name': name})
        if len(movie) == 0:
            print('%s not found' % name)
            return None
        if len(movie) > 1:
            print('Multiple movies with this name')
            return None
        return cast(Movie, movie[0])

    def find_movie_gross(self, name: str) -> None:
        movie = self._find_movie(name)
        if movie and isinstance(movie, Movie):
            print(movie.total_grossing)

    def find_movies_actor_worked_in(self, name: str) -> None:
        actor = self.graph.query_nodes({'type': EntityType.ACTOR, 'name': name})
        if len(actor) == 0:
            print('%s not found' % name)
            return
        if len(actor) > 1:
            print('Multiple actors with this name')
            return
        for edge in actor[0].get_edges():
            for peer in edge.ends:
                if peer.type == EntityType.MOVIE:
                    print(peer.name)

    def list_actors_in_movie(self, name: str) -> None:
        movie = self._find_movie(name)
        if movie:
            for edge in movie.get_edges():
                for peer in edge.ends:
                    if peer.type == EntityType.ACTOR:
                        print(peer.name)

    def top_actor_grossing_value(self, n: str) -> None:
        if n.isdigit():
            number = int(n)
            actors = cast(List[Actor],
                          self.graph.query_nodes({'type': EntityType.ACTOR}))
            sorted_actors = sorted(actors, key=lambda actor: actor.grossing,
                                   reverse=True)
            for i in range(min(len(sorted_actors), number)):
                actor = cast(Actor, sorted_actors[i])
                print('%s has value of %.02f' % (actor.name, actor.grossing))
        else:
            print('Input a valid number')

    def oldest_actors(self, n: str) -> None:
        if n.isdigit():
            number = int(n)
            actors = cast(List[Actor],
                          self.graph.query_nodes({'type': EntityType.ACTOR}))
            sorted_actors = sorted(actors, key=lambda actor: actor.age,
                                   reverse=True)
            for i in range(min(len(sorted_actors), number)):
                actor = cast(Actor, sorted_actors[i])
                print('%s is %d years old' % (actor.name, actor.age))
        else:
            print('Input a valid number')

    def _get_movies_of_year(self, year: int) -> List[Movie]:
        movies = self.graph.query_nodes(
            {'type': EntityType.MOVIE, 'year': year})
        return cast(List[Movie], movies)

    def get_movie_of_year(self, year: str) -> None:
        if year.isdigit():
            movies = self._get_movies_of_year(int(year))
            for movie in movies:
                print(movie.name)
        else:
            print('Input a valid number')

    def get_actor_of_year(self, year: str) -> None:
        if year.isdigit():
            movies = self._get_movies_of_year(int(year))
            for movie in movies:
                for edge in movie.get_edges():
                    for peer in edge.ends:
                        if peer.type == EntityType.ACTOR:
                            print(peer.name)
        else:
            print('Input a valid number')
