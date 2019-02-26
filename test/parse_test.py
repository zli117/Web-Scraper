import os

import pytest
from bs4 import BeautifulSoup

from scraper.spider.parsing_strategy import parse_infobox


@pytest.mark.parametrize('file_name, key_words', [
    ('movie1.html',
     ['Directed by', 'Produced by', 'Written by', 'Based on', 'Starring',
      'Music by', 'Edited by', 'Distributed by', 'Release date', 'Running time',
      'Country', 'Language', 'Budget', 'Box office']),
    ('movie2.html',
     ['Chinese', 'Directed by', 'Produced by', 'Written by', 'Based on',
      'Starring', 'Music by', 'Edited by', 'Distributed by', 'Release date',
      'Running time', 'Country', 'Language', 'Budget', 'Box office']),
    ('actor1.html',
     ['Born', 'Died', 'Years active', 'Spouse(s)', 'Children', 'Relatives']),
    ('tv1.html',
     ['Genre', 'Created by', 'Developed by', 'Directed by', 'Starring',
      'Opening theme', 'Composer(s)', 'Producer(s)', 'Running time',
      'Distributor', 'Original network']),
])
def test_parse_infobox(file_name, key_words):
    with open(os.path.join('test/test_files', file_name)) as html:
        infobox = BeautifulSoup(html).find_all('table', class_='infobox')[0]
        info_dict = parse_infobox(infobox)
        for key_word in key_words:
            assert key_word in info_dict.keys()
