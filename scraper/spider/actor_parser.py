import logging
import re
from typing import Dict, List
from urllib import parse

from bs4.element import Tag

from scraper.graph.actor import Actor
from scraper.graph.base_objects import Url

logger = logging.getLogger('Web-Scraper')


class ActorParser:
    def __init__(self, url: Url):
        self.url = url

    def parse_actor_object(self, infobox: Dict[str, Tag]) -> Actor:
        unquoted_url = parse.unquote(self.url)
        entity_name = unquoted_url.split('/')[-1].replace('_', ' ')
        actor = Actor(name=entity_name, url=self.url)

        age_pattern = re.compile('.*\\(aged? ([0-9]+)\\)')
        # TODO: Refactor this
        if 'Born' in infobox:
            extracted = age_pattern.match(
                str(infobox['Born']).replace(u'\xa0', u' '))
            if extracted:
                age_str = extracted.group(1)
                actor.age = int(age_str)
                return actor

        if 'Died' in infobox:
            extracted = age_pattern.match(
                str(infobox['Died']).replace(u'\xa0', u' '))
            if extracted:
                age_str = extracted.group(1)
                actor.age = int(age_str)
                return actor

        logger.log(logging.WARN, 'Age not found for actor %s' % self.url)
        return actor

    def parse_related_movies(self, html: Tag) -> List[Url]:
        urls = []
        filmography_sections = html.find_all('span', id='Filmography')
        if len(filmography_sections) != 1:
            logger.log(logging.WARN,
                       'Filmography section not found for actor %s' % self.url)
            return []
        filmography: Tag = filmography_sections[0].parent
        table = None
        for sibling in filmography.next_siblings:
            if sibling.name == 'h3':
                headline_span: Tag = sibling.find_all('span', id='Film')
                # We found the headline for the film table
                if (len(headline_span) == 1
                        and 'film' in headline_span[0].string.lower()):
                    found = False
                    for next_siblings in sibling.next_siblings:
                        if (hasattr(next_siblings, 'name')
                                and next_siblings.name == 'table'):
                            table = next_siblings
                            found = True
                            break
                    if found:
                        break
        if table:
            for tr in filter(lambda tr: hasattr(tr, 'contents'), table.tbody):
                for td in filter(lambda td: hasattr(td, 'find_all'),
                                 tr.contents):
                    link = td.find_all('a', href=re.compile('/wiki/'))
                    if len(link) == 1:
                        urls.append(link[0].attrs['href'])
                        break
        return urls
