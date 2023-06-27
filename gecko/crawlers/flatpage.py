import os
import re
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup, Tag
from lxml.html.clean import Cleaner

from .crawler import Crawler
from .helpers import has_class


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
                      remove_unknown_tags=True,
                      safe_attrs_only=True,
                      safe_attrs=frozenset(['src', 'color', 'href', 'title', 'class', 'name', 'id']),
                      remove_tags=('blockquote', 'span', 'font', 'div')
                      )

    return cleaner.clean_html(dirty_html)


def sanitize_title(title):
    return re.sub(r'\s+', ' ', title).strip()


def extract_path(file_path: str, header: Tag):
    if header.select_one('a').has_attr('name'):
        return file_path + '#' + header.select_one('a').get('name')

    if header.select_one('a').has_attr('id'):
        return file_path + '#' + header.select_one('a').get('id')

    return file_path + header.select_one('a').get('href')


class FlatPage(Crawler):
    def crawl(self, library_key: str) -> dict:
        sections = {}
        index_path = self._boost_root / 'libs' / library_key / 'index.html'

        links_to_scrape = set([str(index_path)])
        scraped_links = set()

        while len(links_to_scrape) > 0:
            link = links_to_scrape.pop()
            scraped_links.add(link)

            releative_links = self._scrape_html_file(file_path=link, library_key=library_key, sections=sections)

            for link in releative_links:
                # remvoe anchor
                link = urlparse(link).path

                if not link.endswith(".html") and not link.endswith(".htm"):
                    continue

                if library_key not in link.lower() and library_key.replace('_', '') not in link.lower():
                    continue

                if link not in scraped_links:
                    links_to_scrape.add(link)

        return sections

    def _scrape_html_file(self, file_path: str, library_key: str, sections: dict) -> set:
        if not os.path.isfile(file_path):
            print("File doesn't exis", file_path)
            return []

        with open(file_path, 'rb') as file:
            # sanitize_html fixes errors in handwritten HTML
            soup = BeautifulSoup(sanitize_html(file.read()), 'html.parser')

            headers = [
                anchor.parent
                for anchor in soup.select(
                    'body > h2 > a, body > h3 > a, body > h4 > a, .section-body > h2 > a, .section-body > h3 > a, .section-body > h4 > a')]

            lvl0 = []
            if library_key == 'filesystem' and soup.select_one('body > h1'):
                lvl0 = [{'title': sanitize_title(soup.select_one('body > h1').text), 'path': file_path}]

            last_h2 = None
            last_h3 = None

            for header, next_header in zip(headers, headers[1:] + headers[: 1]):
                if header.name == 'h2':
                    last_h2 = header

                if header.name == 'h3':
                    last_h3 = header

                content = ''
                for sibling in header.next_siblings:
                    if sibling.name == 'ol':
                        continue
                    if sibling == next_header:
                        break
                    content += sibling.get_text().strip() + ' '

                if header.name == 'h2' or not last_h2:
                    lvls = lvl0 + [{'title': sanitize_title(header.text), 'path': extract_path(file_path, header)}]
                elif header.name == 'h3' or not last_h3:
                    lvls = lvl0 + [
                        {'title': sanitize_title(last_h2.text), 'path': extract_path(file_path, last_h2)},
                        {'title': sanitize_title(header.text), 'path': extract_path(file_path, header)}
                    ]
                else:
                    lvls = lvl0 + [
                        {'title': sanitize_title(last_h2.text), 'path': extract_path(file_path, last_h2)},
                        {'title': sanitize_title(last_h3.text), 'path': extract_path(file_path, last_h3)},
                        {'title': sanitize_title(header.text), 'path': extract_path(file_path, header)}
                    ]

                sections[extract_path(file_path, header)] = {'lvls': lvls, 'content': content}

            # collect all releative links to scrape
            releative_links = []
            for link in soup.select('a:not([href^="http"])'):
                releative_links.append(urljoin(file_path, link.get('href')))

            return releative_links
