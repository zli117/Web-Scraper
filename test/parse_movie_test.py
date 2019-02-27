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
                          ('movie5.html', 'Making Mr. Right', 1987, 1584970),
                          ('movie6.html', 'Titanic (1997 film)', 1997, 2)])
def test_movie_parser(file_name, name, year, grossing):
    with open(os.path.join('test/test_files', file_name)) as html:
        infobox = BeautifulSoup(html, 'html.parser').find_all(
            'table', class_='infobox')[0]
        infobox_dict = parse_infobox(infobox)
        url = 'test/%s' % (name.replace(' ', '_'))
        movie_parser = MovieParser(url)
        movie = movie_parser.parse_movie_object(infobox_dict)
        assert name == movie.name
        assert year == movie.year
        assert grossing == movie.total_grossing


@pytest.mark.parametrize('file_name, name, num_starring',
                         [('movie3.html', 'Uncle Buck', 2),
                          ('movie1.html',
                           'How to Train Your Dragon: The Hidden World', 5),
                          ('movie2.html', 'The Wandering Earth', 4),
                          ('movie4.html', 'JFK', 9),
                          ('movie6.html', 'Titanic (1997 film)', 10)])
def test_movie_starring(file_name, name, num_starring):
    with open(os.path.join('test/test_files', file_name)) as html:
        url = 'test/%s' % (name.replace(' ', '_'))
        movie_parser = MovieParser(url)
        infobox = BeautifulSoup(html, 'html.parser').find_all(
            'table', class_='infobox')[0]
        infobox_dict = parse_infobox(infobox)
        stars = movie_parser.parse_staring(infobox_dict)
        assert num_starring == len(stars)
        for star in stars:
            assert star is not None


@pytest.mark.parametrize('file_name, name, num_casting',
                         [('movie3.html', 'Uncle Buck', 10),
                          ('movie1.html',
                           'How to Train Your Dragon: The Hidden World', 16),
                          ('movie2.html', 'The Wandering Earth', 5),
                          ('movie4.html', 'JFK', 34),
                          ('movie5.html', 'Making Mr. Right', 0),
                          ('movie6.html', 'Titanic (1997 film)', 10)])
def test_movie_casting(file_name, name, num_casting):
    with open(os.path.join('test/test_files', file_name)) as html:
        url = 'test/%s' % (name.replace(' ', '_'))
        movie_parser = MovieParser(url)
        soup = BeautifulSoup(html, 'html.parser')
        casts = movie_parser.parse_cast(soup.html)
        assert num_casting == len(casts)
        print(casts)
        for cast in casts:
            assert cast is not None
