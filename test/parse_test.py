import os

import pytest
from bs4 import BeautifulSoup

from scraper.spider.utils import (PageType, parse_infobox, parse_page_type)

from scraper.spider.parse_actor import ParseActor


@pytest.mark.parametrize('file_name, key_words', [
    ('movie1.html',
     ['Directed by', 'Produced by', 'Written by', 'Based on', 'Starring',
      'Music by', 'Edited by', 'Distributed by', 'Release date', 'Running time',
      'Country', 'Language', 'Budget', 'Box office', '_image_caption']),
    ('movie2.html',
     ['Chinese', 'Directed by', 'Produced by', 'Written by', 'Based on',
      'Starring', 'Music by', 'Edited by', 'Distributed by', 'Release date',
      'Running time', 'Country', 'Language', 'Budget', 'Box office',
      '_image_caption']),
    ('actor1.html',
     ['Born', 'Died', 'Years active', 'Spouse(s)', 'Children', 'Relatives']),
    ('actor2.html',
     ['Born', 'Died', 'Years active', 'Occupation', 'Children']),
    ('actor4.html',
     ['Born', 'Years active', 'Occupation', 'Children']),
    ('tv1.html',
     ['Genre', 'Created by', 'Developed by', 'Directed by', 'Starring',
      'Opening theme', 'Composer(s)', 'Producer(s)', 'Running time',
      'Distributor', 'Original network']),
])
def test_parse_infobox(file_name, key_words):
    with open(os.path.join('test/test_files', file_name)) as html:
        infobox = BeautifulSoup(html, 'html.parser').find_all(
            'table', class_='infobox')[0]
        info_dict = parse_infobox(infobox)
        for key_word in key_words:
            assert key_word in info_dict.keys()


@pytest.mark.parametrize('file_name, page_type',
                         [('movie1.html', PageType.MOVIE),
                          ('movie2.html', PageType.MOVIE),
                          ('actor2.html', PageType.ACTOR),
                          ('tv1.html', PageType.OTHER)])
def test_page_type_parser(file_name, page_type):
    with open(os.path.join('test/test_files', file_name)) as html:
        infobox = BeautifulSoup(html, 'html.parser').find_all(
            'table', class_='infobox')[0]
        infobox_dict = parse_infobox(infobox)
        assert page_type == parse_page_type(infobox_dict)


@pytest.mark.parametrize('file_name, name, age',
                         [('actor3.html', 'Jay Baruchel', 36),
                          ('actor1.html', 'Kelly Lai Chen', 84),
                          ('actor2.html', 'Jean Simmons', 80),
                          ('actor4.html', 'Cate Blanchett', 49)])
def test_actor_parser(file_name, name, age):
    with open(os.path.join('test/test_files', file_name)) as html:
        actor_parser = ParseActor()
        infobox = BeautifulSoup(html, 'html.parser').find_all(
            'table', class_='infobox')[0]
        infobox_dict = parse_infobox(infobox)
        url = 'test/%s' % (name.replace(' ', '_'))
        actor = actor_parser.parse_actor_object(url, infobox_dict)
        assert age == actor.age
        assert url == actor.url
        assert name == actor.name


@pytest.mark.parametrize('file_name, num_films',
                         [('actor3.html', 36),
                          ('actor5.html', 26),
                          ('actor6.html', 33)])
def test_actor_parser(file_name, num_films):
    with open(os.path.join('test/test_files', file_name)) as html:
        actor_parser = ParseActor()
        soup = BeautifulSoup(html, 'html.parser')
        movies = actor_parser.parse_related_movies(soup.html)
        assert num_films == len(movies)
