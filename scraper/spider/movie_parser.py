import logging
import re
from typing import Dict, List
from urllib import parse

from bs4.element import Tag

from scraper.graph.base_objects import Url
from scraper.graph.movie import Movie

logger = logging.getLogger('Web-Scraper')

CURRENCY_CONVERSION = {'$': 1}

UNIT_CONVERSION = {'million': 1e6, 'billion': 1e9}


class MovieParser:
    """
    Parser for movie
    """
    def __init__(self, url: Url):
        self.url = url

    def parse_movie_object(self, infobox: Dict[str, Tag]) -> Movie:
        """
        Parse and construct movie object
        Args:
            infobox: The infobox dict

        Returns:
            movie object
        """
        unquoted_url = parse.unquote(self.url)
        entity_name = unquoted_url.split('/')[-1].replace('_', ' ')
        movie = Movie(name=entity_name, url=self.url)

        # Refactor this
        year_pattern = re.compile('([0-9][0-9][0-9][0-9])')
        if 'Release date' in infobox:
            tag = infobox['Release date']
            tag_str = str(tag).replace(u'\xa0', u' ')
            matched_year = year_pattern.search(tag_str)
            if matched_year:
                year = int(matched_year.group(0))
                movie.year = year
            else:
                logger.log(logging.WARN, 'Year not found for %s' % self.url)
        else:
            currency = logger.log(logging.WARN,
                                  'Release date not found for %s' % self.url)

        grossing_pattern = re.compile(
            '(\\$)([1-9][0-9]*(\\.[0-9]+)?) ((million)|(billion))')
        grossing_pattern_2 = re.compile(
            '(\\$)(([1-9]|[1-9][0-9]|[1-9][0-9][0-9])(,[0-9][0-9][0-9])*)\\D')
        if 'Box office' in infobox:
            tag = infobox['Box office']
            tag_str = str(tag).replace(u'\xa0', u' ')
            matched_grossing = (grossing_pattern.search(tag_str)
                                or grossing_pattern_2.search(tag_str))
            if matched_grossing:
                grossing = float(matched_grossing.group(2).replace(',', ''))
                currency = matched_grossing.group(1)
                converted_value = CURRENCY_CONVERSION.get(currency,
                                                          1) * grossing
                unit = UNIT_CONVERSION.get(matched_grossing.group(4), 1)
                movie.total_grossing = converted_value * unit
            else:
                logger.error('Money format not recognized for %s' % self.url)
        else:
            logger.log(logging.WARN, 'Box office not found for %s' % self.url)

        return movie

    def parse_staring(self, infobox: Dict[str, Tag]) -> List[Url]:
        """
        Parse the list of staring actors
        Args:
            infobox: The infobox

        Returns:
            A list of actors
        """
        urls = []
        if 'Starring' in infobox:
            for link in infobox['Starring'].find_all(
                    'a', href=re.compile('/wiki/')):
                urls.append(link.attrs['href'])
        else:
            logger.log(logging.WARN, 'Starring not found for %s' % self.url)

        return urls

    def parse_cast(self, html: Tag) -> List[Url]:
        """
        Parse the list of casting actors
        Args:
            html: The page

        Returns:
            A list of actors
        """
        urls: List[Url] = []
        cast_h2 = html.find_all(
            lambda tag: tag.name == 'h2' and tag.find_all('span', id='Cast'))
        if len(cast_h2) != 1:
            logger.log(logging.WARN,
                       '%d cast section found for %s' % (
                           len(cast_h2), self.url))
            return urls
        cast_list = None
        for sibling in cast_h2[0].next_siblings:
            if hasattr(sibling, 'name') and sibling.name == 'ul':
                cast_list = sibling
                break
            elif (hasattr(sibling, 'name') and sibling.name == 'div'
                  and sibling.ul is not None):
                cast_list = sibling.ul
                break
        if cast_list:
            for li in cast_list.find_all('li'):
                link = li.find('a', href=re.compile('/wiki/'))
                if link:
                    urls.append(link.attrs['href'])
        else:
            logger.log(logging.WARN, 'No cast list for %s' % self.url)
            pass

        return urls
