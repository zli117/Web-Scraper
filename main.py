import argparse
import logging
import sys
from typing import cast

from tqdm import tqdm

from scraper.graph.base_objects import Url
from scraper.graph.graph import Graph
from scraper.graph.shell import ShellRunner
from scraper.spider.spider_runner import SpiderRunner

COLORS = {
    'WARNING': '\033[93m',
    'DEBUG': '\033[94m',
    'ERROR': '\033[91m'
}


class TqdmHandler(logging.StreamHandler):
    def __init__(self):
        logging.StreamHandler.__init__(self)

    def emit(self, record):
        level = record.levelname
        msg = self.format(record)
        if level in COLORS:
            msg = '%s%s\033[0m' % (COLORS[level], msg)
        tqdm.write(msg)


logging_formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger('Web-Scraper')

tqdm_handler = TqdmHandler()
tqdm_handler.setFormatter(logging_formatter)
logger.addHandler(tqdm_handler)
logger.setLevel(logging.INFO)

if __name__ == '__main__':
    parser = argparse.ArgumentParser('Movie Scraper')
    parser.add_argument('-o', '--out', type=str,
                        help='Path to save the json file', default='out.json')
    parser.add_argument('-f', '--file', type=str, help='Path to a json file')
    parser.add_argument('-a', '--actors', type=int,
                        help='Number of actors to scrape', default=250)
    parser.add_argument('-m', '--movies', type=int,
                        help='Number of movies to scrape', default=125)
    parser.add_argument('-s', '--start', type=str, help='Starting url',
                        default='/wiki/Titanic_(1997_film)')
    if len(sys.argv) == 1:
        parser.print_help()
        exit()
    args = parser.parse_args()

    if args.file is not None:
        graph = Graph()
        with open(args.file, 'r') as f:
            if not graph.deserialize(f.read()):
                logger.error('Invalid json file')
    else:
        spider = SpiderRunner(cast(Url, '/wiki/Titanic_(1997_film)'),
                              actor_limit=args.actors, movie_limit=args.movies)
        spider.run()
        spider.save(args.out)
        graph = spider.graph

    shell = ShellRunner(graph)
    shell.start()
