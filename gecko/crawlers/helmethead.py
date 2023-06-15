import re

from bs4 import BeautifulSoup, Tag

from .crawler import Crawler
from .helpers import has_class


def sanitize_title(title):
    return re.sub(r'\s+', ' ', title).strip()


def scrape_section(section: Tag, sections: dict, lvls: list, html_file_path: str):
    heading = section.select_one('h1, h2, h3, h4')

    if section.has_attr('id'):
        id = section.get('id')
    else:
        id = heading.find('a').get('id')

    title = sanitize_title(heading.text)
    path = html_file_path + '#' + id
    lvls = lvls + [{'title': title, 'path': path}]

    content = ''
    for elm in heading.next_siblings:
        if has_class(elm, 'section'):
            break
        content += elm.get_text().strip() + ' '

    sections[path] = {'lvls': lvls, 'content': content}

    for section in section.find_all('div', class_='section', recursive=False):
        scrape_section(section, sections, lvls, html_file_path)


class Helmethead(Crawler):
    def crawl(self, library_key: str) -> dict:
        assert library_key == 'iterator' or library_key == 'graph_parallel' or library_key == 'ptr_container'

        doc_path = self._boost_root / 'libs' / library_key / 'doc'
        if library_key == 'graph_parallel':
            doc_path = doc_path / 'html'

        sections = {}
        for html_file_path in doc_path.glob('*.html'):
            with open(html_file_path, 'r', encoding='utf-8', errors='ignore') as file:
                soup = BeautifulSoup(file.read(), 'html.parser')

                lvls = []
                document = soup.select_one('body > div.document')

                if not document:
                    continue

                heading = document.select_one('h1.title')
                sub_heading = document.select_one('h2:first-of-type.subtitle')
                if sub_heading:
                    heading = sub_heading

                if heading and 'Pointer Container Library' not in heading.text:
                    lvls = [{'title': sanitize_title(heading.text), 'path': str(html_file_path)}]
                    content = ''
                    for elm in heading.next_siblings:
                        if has_class(elm, 'docinfo'):
                            continue
                        if has_class(elm, 'docutils'):
                            continue
                        if has_class(elm, 'topic'):
                            continue
                        if has_class(elm, 'section'):
                            break
                        content += elm.get_text().strip() + ' '
                    sections[str(html_file_path)] = {'lvls': lvls, 'content': content}

                for section in document.find_all('div', class_='section', recursive=False):
                    scrape_section(section, sections, lvls, str(html_file_path))

        return sections
