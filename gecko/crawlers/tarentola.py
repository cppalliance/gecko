import re
from bs4 import BeautifulSoup, Tag

from .crawler import Crawler
from .helpers import has_class


class Tarentola(Crawler):
    def crawl(self, library_key: str) -> dict:
        assert library_key == 'parameter' or library_key == 'parameter_python'
        sections = {}
        html_dir = self._boost_root / 'libs' / library_key / 'doc/html'

        for html_file_path in html_dir.glob('*.html'):
            with open(html_file_path, 'r', encoding='utf-8', errors='ignore') as file:
                soup = BeautifulSoup(file.read(), 'html.parser')
                for sect1 in soup.select('body .document > .section'):
                    self._extract_section_n(str(html_file_path), sections, sect1)

        return sections

    def _extract_section_n(self, html_file_path: str, sections: dict, sect: Tag, lvls: list = []):
        header = sect.select_one('h1, h2, h3, h4, h5, h6')

        title = re.sub(r'^([\d.]+)', ' ', header.text).strip()
        path = html_file_path + '#' + header.find_parent(class_='section').get('id')

        # regex removes section and subsection numbers
        lvls = lvls + [{'title': title, 'path': path}]

        if header.find_next_sibling() and has_class(header.find_next_sibling(), 'section'):
            siblings = header.find_next_sibling().find_all(recursive=False)
        else:
            siblings = header.find_next_siblings()

        content = ''
        for sibling in siblings:
            if has_class(sibling, 'section'):
                self._extract_section_n(html_file_path, sections, sibling, lvls)
                continue
            content += sibling.get_text() + ' '

        sections[path] = {'content': content, 'lvls': lvls}
