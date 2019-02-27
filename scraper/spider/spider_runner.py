from queue import LifoQueue, Queue
from typing import Dict, Type, cast
from urllib import parse, request

from bs4 import BeautifulSoup
from bs4.element import Tag

from scraper.graph.base_objects import EntityType, Url
from scraper.graph.graph import Graph
from scraper.graph.movie import Movie
from scraper.spider.actor_parser import ActorParser
from scraper.spider.movie_parser import MovieParser
from scraper.spider.utils import PageType, parse_page_type_get_infobox


class SpiderRunner:
    _URL_PREFIX = 'https://en.wikipedia.org'

    def __init__(self, init_url: Url, actor_limit: int = -1,
                 movie_limit: int = -1, queue: Type[Queue] = LifoQueue) -> None:
        """
        Create a spider runner.
        Args:
            init_url: Has to be a url to a movie.
        """
        self.init_url = init_url
        self.graph = Graph()
        self.actor_parser = ActorParser()
        self.movie_parser = MovieParser()
        # Contains tuple of (url, predecessor, weight)
        self.queue = queue()
        self.queue.put((init_url, None, 0))
        self.actor_limit = actor_limit
        self.movie_limit = movie_limit

    @staticmethod
    def get_full_url(url: Url) -> Url:
        return cast(Url, parse.urljoin(SpiderRunner._URL_PREFIX, url))

    def _process_movie(self, url: Url, html: Tag,
                       infobox: Dict[str, Tag]) -> None:
        movie = self.movie_parser.parse_movie_object(url, infobox)
        if self.graph.add_node(movie):
            stars = self.movie_parser.parse_staring(infobox)
            casts = self.movie_parser.parse_cast(html)
            total_actors = stars
            actors_added = set(total_actors)
            # Distribute weight according to the order
            print('cast: ', casts)
            print('star: ', stars)
            for actor in casts:
                if actor not in actors_added:
                    total_actors.append(actor)
                    actors_added.add(actor)
            total_weight_units = (1 + len(total_actors)) * len(total_actors) / 2
            for i, actor in enumerate(reversed(total_actors)):
                self.queue.put((actor, movie, (i + 1) / total_weight_units))

    def _process_actor(self, url: Url, html: Tag, infobox: Dict[str, Tag],
                       predecessor: Movie, weight: float) -> None:
        actor = self.actor_parser.parse_actor_object(url, infobox)
        if self.graph.add_node(actor):
            if predecessor:
                edge = self.graph.add_relationship(
                    predecessor.node_id, actor.node_id)
                if edge:
                    edge.weight = weight
            movies = self.actor_parser.parse_related_movies(html)
            for movie in movies:
                self.queue.put((movie, None, 0))

    def run(self):
        while not self.queue.empty():
            url, predecessor, weight = self.queue.get()
            print(url, predecessor, weight)
            if self.graph.check_node_exist(url):
                continue
            full_url = self.get_full_url(url)
            soup = BeautifulSoup(request.urlopen(full_url))
            page_type, infobox = parse_page_type_get_infobox(soup.html)
            if page_type == PageType.ACTOR:
                self._process_actor(url, soup.html, infobox, predecessor,
                                    weight)
            elif page_type == PageType.MOVIE:
                self._process_movie(url, soup.html, infobox)
            string = 'actor: %d, movie: %d' % (
                self.graph.num_node(EntityType.ACTOR),
                self.graph.num_node(EntityType.MOVIE))
            print('\033[93m' + string + '\033[0m')
            if (0 < self.actor_limit < self.graph.num_node(EntityType.ACTOR)
                    and 0 < self.movie_limit < self.graph.num_node(
                        EntityType.MOVIE)):
                break

    def save(self, out_file: str) -> None:
        json_str = self.graph.serialize()
        with open(out_file, 'w') as f:
            f.write(json_str)
