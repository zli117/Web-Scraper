import os

import pytest
from bs4 import BeautifulSoup

from scraper.spider.movie_parser import MovieParser
from scraper.spider.utils import parse_infobox


@pytest.mark.parametrize('file_name, name, year, grossing',
                         [('movie3.html', 'Uncle Buck', 1989, 79.2),
                          ('movie1.html',
                           'How to Train Your Dragon: The Hidden World', 2019,
                           274.9),
                          ('movie2.html', 'The Wandering Earth', 2019, 650)])
def test_movie_parser(file_name, name, year, grossing):
    with open(os.path.join('test/test_files', file_name)) as html:
        movie_parser = MovieParser()
        infobox = BeautifulSoup(html, 'html.parser').find_all(
            'table', class_='infobox')[0]
        infobox_dict = parse_infobox(infobox)
        url = 'test/%s' % (name.replace(' ', '_'))
        movie = movie_parser.parse_movie_object(url, infobox_dict)
        assert name == movie.name
        assert year == movie.year
        assert grossing == movie.total_grossing
