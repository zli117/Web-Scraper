import re
from enum import Enum
from typing import Dict, List, Optional

from bs4.element import Tag

from scraper.graph.actor import Actor
from scraper.graph.base_objects import Url


class PageType(Enum):
    MOVIE = 0
    ACTOR = 1
    OTHER = 2


def parse_infobox(infobox: Tag) -> Dict[str, Tag]:
    entries = list(filter(lambda e: isinstance(e, Tag), infobox.tbody.contents))
    entry_dict = {}
    # First find image caption:
    index = 0
    while index < len(entries):
        entry = entries[index]
        links = entry.find_all('a', class_='image')
        found = False
        if len(links) == 1:
            img_link: Tag = links[0]
            for sibling in img_link.next_siblings:
                if sibling.name == 'div' and sibling.string is not None:
                    entry_dict['_image_caption'] = sibling.string.strip()
                    found = True
                    break
        else:
            tds = entry.find_all('td')
            # If we have already reached td, then that means there's no image
            if tds:
                break
        index += 1
        if found:
            break

    # Find entries
    while index < len(entries):
        entry = entries[index]
        if entry.find_all('th') and entry.find_all('td'):
            if entry.th.string is not None:
                key = entry.th.string.strip().replace(u'\xa0', u' ')
                entry_dict[key] = entry.td
            elif entry.th.div is not None and entry.th.div.string is not None:
                key = entry.th.div.string.strip().replace(u'\xa0', u' ')
                entry_dict[key] = entry.td
            elif entry.th.a is not None and entry.th.a.string is not None:
                key = entry.th.a.string.strip().replace(u'\xa0', u' ')
                entry_dict[key] = entry.td
        index += 1

    return entry_dict


def parse_page_type(infobox: Dict[str, Tag]) -> PageType:
    # Check if movie
    image_caption = infobox.get('_image_caption', '')
    if 'theatrical release poster' in image_caption.lower():
        return PageType.MOVIE

    # Check if actor
    if 'Occupation' in infobox:
        occupation = infobox['Occupation']
        if occupation(text=re.compile('(Actor|actor|Actress|actress)')):
            return PageType.ACTOR

    return PageType.OTHER


class ParseActor:
    @staticmethod
    def parse_actor_object(url: Url,
                           infobox: Dict[str, Tag]) -> Optional[Actor]:
        entity_name = url.split('/')[-1].replace('_', ' ')
        actor = Actor(name=entity_name, url=url)

        age_pattern = re.compile('.*\\(aged? ([0-9]+)\\)')
        # TODO: Refactor this
        if 'Born' in infobox:
            extracted = age_pattern.match(
                str(infobox['Born']).replace(u'\xa0', u' '))
            if extracted:
                age_str = extracted.group(1)
                print(age_str)
                if age_str.isdigit():
                    actor.age = int(age_str)
                    return actor
                else:
                    # TODO: Logging here and return
                    return None

        if 'Died' in infobox:
            extracted = age_pattern.match(
                str(infobox['Died']).replace(u'\xa0', u' '))
            if extracted:
                age_str = extracted.group(1)
                print(age_str)
                if age_str.isdigit():
                    actor.age = int(age_str)
                    return actor
                else:
                    # TODO: Logging here and return
                    return None

        # TODO: Logging here
        return None

    @staticmethod
    def parse_related_movies(html: Tag) -> List[Url]:
        return []
