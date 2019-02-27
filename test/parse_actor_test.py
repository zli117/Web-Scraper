import os

import pytest
from bs4 import BeautifulSoup

from scraper.spider.actor_parser import ActorParser
from scraper.spider.utils import parse_infobox


@pytest.mark.parametrize('file_name, name, age',
                         [('actor3.html', 'Jay Baruchel', 36),
                          ('actor1.html', 'Kelly Lai Chen', 84),
                          ('actor2.html', 'Jean Simmons', 80),
                          ('actor4.html', 'Cate Blanchett', 49)])
def test_actor_parser(file_name, name, age):
    with open(os.path.join('test/test_files', file_name)) as html:
        infobox = BeautifulSoup(html, 'html.parser').find_all(
            'table', class_='infobox')[0]
        infobox_dict = parse_infobox(infobox)
        url = 'test/%s' % (name.replace(' ', '_'))
        actor_parser = ActorParser(url)
        actor = actor_parser.parse_actor_object(infobox_dict)
        assert age == actor.age
        assert url == actor.url
        assert name == actor.name


@pytest.mark.parametrize('file_name, name, num_films',
                         [('actor3.html', 'Jay Baruchel', 36),
                          ('actor5.html', 'Craig Ferguson', 26),
                          ('actor6.html', 'Laurie Metcalf', 33)])
def test_actor_movie_parser(file_name, name, num_films):
    with open(os.path.join('test/test_files', file_name)) as html:
        url = 'test/%s' % (name.replace(' ', '_'))
        actor_parser = ActorParser(url)
        soup = BeautifulSoup(html, 'html.parser')
        movies = actor_parser.parse_related_movies(soup.html)
        assert num_films == len(movies)
        for movie in movies:
            assert movie is not None
