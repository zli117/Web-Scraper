import re
from typing import Dict, List

from bs4.element import Tag

from scraper.graph.base_objects import Url
from scraper.graph.movie import Movie


class MovieParser:
    @staticmethod
    def parse_movie_object(url: Url, infobox: Dict[str, Tag]) -> Movie:
        entity_name = url.split('/')[-1].replace('_', ' ')
        movie = Movie(name=entity_name, url=url)

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
                # TODO: Log
                pass
        else:
            # TODO: Log
            pass

        grossing_pattern = re.compile('\\$([1-9][0-9]*(\\.[0-9]+)?) million')
        grossing_pattern_2 = re.compile(
            '\\$(([1-9]|[1-9][0-9]|[1-9][0-9][0-9])(,[0-9][0-9][0-9])*)\D')
        if 'Box office' in infobox:
            tag = infobox['Box office']
            tag_str = str(tag).replace(u'\xa0', u' ')
            matched_grossing = (grossing_pattern.search(tag_str)
                                or grossing_pattern_2.search(tag_str))
            print(matched_grossing.group(1))
            if matched_grossing:
                grossing = float(matched_grossing.group(1).replace(',', ''))
                movie.total_grossing = grossing
            # TODO: Log
        else:
            # TODO: Log
            pass

        return movie

    @staticmethod
    def parse_staring(infobox: Dict[str, Tag]) -> List[Url]:
        urls = []
        if 'Starring' in infobox:
            for link in infobox['Starring'].find_all(
                    'a', href=re.compile('/wiki/')):
                urls.append(link.href)
        else:
            # TODO: Log
            pass

        return urls

    @staticmethod
    def parse_cast(html: Tag) -> List[Url]:
        urls = []
        cast_h2 = html.find_all(
            lambda tag: tag.name == 'h2' and tag.find_all('span', id='Cast'))
        if len(cast_h2) != 1:
            # TODO: Log
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
                    urls.append(link.href)
        else:
            # TODO: Log
            pass

        return urls
