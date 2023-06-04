import re
from bs4 import BeautifulSoup, Tag

from .crawler import Crawler
from .helpers import has_class


class Harlequin(Crawler):
    '''
    A dedicated crawler for numeric/ublas and numeric/interval libraries.
    '''

    def crawl(self, library_key: str) -> dict:
        sections = {}
        html_dir = self._boost_root / 'libs' / library_key / 'doc'

        for html_file_path in list(html_dir.glob('*.html')) + list(html_dir.glob('*.htm')):
            with open(html_file_path, 'r', encoding='utf-8', errors='ignore') as file:
                soup = BeautifulSoup(file.read(), 'html.parser')
                for h2 in soup.select('body > h2[id]'):
                    self._extract_h2_section_that_has_id(str(html_file_path), sections, h2)
                for a in soup.select('body > h2 > a'):
                    self._extract_h2_section_that_has_a_tag(str(html_file_path), sections, a.parent)

        return sections

    def _extract_h2_section_that_has_id(self, html_file_path: str, sections: dict, h2: Tag):
        content = ''
        for sibling in h2.find_next_siblings():
            if sibling.name == 'h2' and sibling.has_attr('id'):
                break
            content += sibling.get_text() + ' '

        sections[html_file_path + '#' + h2.get('id')] = {'content': content, 'lvls': [h2.text]}

    def _extract_h2_section_that_has_a_tag(self, html_file_path: str, sections: dict, h2: Tag):
        content = ''
        for sibling in h2.find_next_siblings():
            if sibling.name == 'h2' and sibling.select_one('a'):
                break
            content += sibling.get_text() + ' '

        if h2.find('a').has_attr('id'):
            id = h2.find('a')['id']
        else:
            id = h2.find('a')['name']

        sections[html_file_path + '#' + id] = {'content': content, 'lvls': [h2.text]}
