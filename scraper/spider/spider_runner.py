import logging
from queue import LifoQueue, Queue
from typing import Dict, Type, cast
from urllib import parse, request

from bs4 import BeautifulSoup
from bs4.element import Tag
from tqdm import tqdm

from scraper.graph.base_objects import EntityType, Url
from scraper.graph.graph import Graph
from scraper.graph.movie import Movie
from scraper.spider.actor_parser import ActorParser
from scraper.spider.movie_parser import MovieParser
from scraper.spider.utils import PageType, parse_page_type_get_infobox

logger = logging.getLogger('Web-Scraper')


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
        parser = MovieParser(url)
        movie = parser.parse_movie_object(infobox)
        if self.graph.add_node(movie):
            stars = parser.parse_staring(infobox)
            casts = parser.parse_cast(html)
            total_actors = stars
            actors_added = set(total_actors)
            # Distribute weight according to the order
            for actor in casts:
                if actor not in actors_added:
                    total_actors.append(actor)
                    actors_added.add(actor)
            total_weight_units = (1 + len(total_actors)) * len(total_actors) / 2
            for i, actor in enumerate(reversed(total_actors)):
                self.queue.put((actor, movie, (i + 1) / total_weight_units))

    def _process_actor(self, url: Url, html: Tag, infobox: Dict[str, Tag],
                       predecessor: Movie, weight: float) -> None:
        parser = ActorParser(url)
        actor = parser.parse_actor_object(infobox)
        if self.graph.add_node(actor):
            if predecessor:
                edge = self.graph.add_relationship(
                    predecessor.node_id, actor.node_id)
                if edge:
                    edge.weight = weight
            movies = parser.parse_related_movies(html)
            for movie in movies:
                self.queue.put((movie, None, 0))

    def run(self):
        with tqdm(total=100) as progress_bar:
            previous_percent = 0
            while not self.queue.empty():
                url, predecessor, weight = self.queue.get()
                logger.log(logging.INFO, url)
                logger.log(logging.DEBUG,
                           '%s %s %s' % (url, predecessor, weight))
                if self.graph.check_node_exist(url):
                    logger.log(logging.DEBUG, 'skip %s' % url)

                actor_parser = ActorParser(url)
                full_url = self.get_full_url(url)
                soup = BeautifulSoup(request.urlopen(full_url), features="lxml")
                page_type, infobox = parse_page_type_get_infobox(soup.html)
                if page_type == PageType.ACTOR:
                    self._process_actor(url, soup.html, infobox, predecessor,
                                        weight)
                elif page_type == PageType.MOVIE:
                    self._process_movie(url, soup.html, infobox)
                num_actors = self.graph.num_node(EntityType.ACTOR)
                num_movies = self.graph.num_node(EntityType.MOVIE)
                progress = 'actor: %d, movie: %d' % (
                    self.graph.num_node(EntityType.ACTOR),
                    self.graph.num_node(EntityType.MOVIE))
                percentage = ((min(num_actors,
                                   self.actor_limit) / self.actor_limit
                               + min(num_movies,
                                     self.movie_limit) / self.movie_limit) / 2)
                progress_bar.update((percentage - previous_percent) * 100)
                previous_percent = percentage
                progress_bar.set_postfix_str(progress)
                if (0 < self.actor_limit < num_actors
                        and 0 < self.movie_limit < num_movies):
                    break

    def save(self, out_file: str) -> None:
        json_str = self.graph.serialize()
        with open(out_file, 'w') as f:
            f.write(json_str)
