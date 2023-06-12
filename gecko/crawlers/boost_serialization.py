import re
from pathlib import Path

from bs4 import BeautifulSoup, Tag
from lxml.html.clean import Cleaner

from .crawler import Crawler
from .helpers import has_class


def sanitize_title(title):
    return re.sub(r'\s+', ' ', title).strip()


def sanitize_html(dirty_html):
    '''
    Handwritten HTML files have all kind of problems like p tags which arn not closed properly.
    This function fix these errors before parsing it with BeautifulSoup
    '''
    cleaner = Cleaner(page_structure=True,
                      meta=True,
                      embedded=True,
                      links=True,
                      style=True,
                      processing_instructions=True,
                      inline_style=True,
                      scripts=True,
                      javascript=True,
                      comments=True,
                      frames=True,
                      forms=True,
                      annoying_tags=True,
                      safe_attrs_only=True,
                      )

    return cleaner.clean_html(dirty_html)


def find_parent_lvls(header: Tag, headers: list, html_file_path: Path):
    parent_tag_name = 'h' + str(int(header.name[1])-1)
    parent = None
    for elm in headers:
        if elm == header:
            break
        if elm.name == parent_tag_name:
            parent = elm

    if parent:
        parent_title = sanitize_title(parent.text)
        parent_url = str(html_file_path) + '#' + parent.a.get('name')
        parent_parent_lvls = find_parent_lvls(parent, headers, html_file_path)
        return parent_parent_lvls + [{'title': parent_title, 'url': parent_url}]

    return []


class BoostSerialization(Crawler):
    def crawl(self, library_key: str) -> dict:
        assert library_key == 'serialization'

        sections = {}
        doc_path = self._boost_root / 'libs' / library_key / 'doc'

        for html_file_path in doc_path.glob('*.html'):

            with open(html_file_path, 'r', encoding='utf-8', errors='ignore') as file:
                # sanitize_html fixes errors in handwritten HTML
                soup = BeautifulSoup(sanitize_html(file.read()), 'html.parser')

                if not soup.select_one('h2[align="center"]'):
                    continue

                lvl0 = [{'title': sanitize_title(soup.select_one(
                    'h2[align="center"]').text), 'url': str(html_file_path)}]

                lvl0_content = ''
                for elm in soup.select_one('h2[align="center"]').find_parent('table').next_siblings:
                    if has_class(elm, 'page-index') or has_class(elm, 'index'):
                        continue
                    if elm.name in ['h2', 'h3', 'h4'] and elm.select_one('a[name]'):
                        break
                    lvl0_content += elm.get_text().strip() + ' '

                sections[html_file_path] = {'lvls': lvl0, 'content': lvl0_content}

                headers = [a.parent for a in soup.select(
                    'body > h2 > a[name], body > h3 > a[name], body > h4 > a[name]')]

                for header, next_header in zip(headers, headers[1:] + headers[: 1]):
                    content = ''
                    for elm in header.next_siblings:
                        if elm == next_header:
                            break
                        content += elm.get_text().strip() + ' '

                    title = sanitize_title(header.text)
                    url = str(html_file_path) + '#' + header.a.get('name')
                    lvls = lvl0 + find_parent_lvls(header, headers, html_file_path) + [{'title': title, 'url': url}]
                    sections[url] = {'lvls': lvls, 'content': content}

        return sections
