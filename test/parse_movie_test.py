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
                          ('movie2.html', 'The Wandering Earth', 2019, 650),
                          ('movie4.html', 'JFK', 1991, 205.4),
                          ('movie5.html', 'Making Mr. Right', 1987, 1584970)])
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


@pytest.mark.parametrize('file_name, num_starring',
                         [('movie3.html', 2),
                          ('movie1.html', 5),
                          ('movie2.html', 4),
                          ('movie4.html', 9)])
def test_movie_starring(file_name, num_starring):
    with open(os.path.join('test/test_files', file_name)) as html:
        movie_parser = MovieParser()
        infobox = BeautifulSoup(html, 'html.parser').find_all(
            'table', class_='infobox')[0]
        infobox_dict = parse_infobox(infobox)
        stars = movie_parser.parse_staring(infobox_dict)
        assert num_starring == len(stars)


@pytest.mark.parametrize('file_name, num_casting',
                         [('movie3.html', 10),
                          ('movie1.html', 16),
                          ('movie2.html', 5),
                          ('movie4.html', 34),
                          ('movie5.html', 0)])
def test_movie_starring(file_name, num_casting):
    with open(os.path.join('test/test_files', file_name)) as html:
        movie_parser = MovieParser()
        soup = BeautifulSoup(html, 'html.parser')
        casts = movie_parser.parse_cast(soup.html)
        assert num_casting == len(casts)
