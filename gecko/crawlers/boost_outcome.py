import os
import re
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from .crawler import Crawler


def sanitize_title(title):
    return re.sub(r'\s+', ' ', title).strip()


class BoostOutcome(Crawler):
    def crawl(self, library_key: str) -> dict:
        assert library_key == 'outcome'
        sections = {}
        index_path = self._boost_root / 'libs' / library_key / 'doc/html' / 'index.html'

        links_to_scrape = set([str(index_path)])
        scraped_links = set()

        while len(links_to_scrape) > 0:
            link = links_to_scrape.pop()
            scraped_links.add(link)

            releative_links = self._scrape_html_file(file_path=link, sections=sections)

            for link in releative_links:
                # remvoe anchor
                link = urlparse(link).path

                if not link.endswith(".html"):
                    continue

                if library_key not in link.lower() and library_key.replace('_', '') not in link.lower():
                    continue

                if link not in scraped_links:
                    links_to_scrape.add(link)

        # here we have access to all links so we can find and populate hierachy
        for _, section in sections.items():
            self._populate_hierachy(sections, section)

        for _, section in sections.items():
            # remove library name (it is at the end)
            section['lvls'].pop()

            section['lvls'].reverse()

        return sections

    def _scrape_html_file(self, file_path: str, sections: dict) -> set:
        if not os.path.isfile(file_path):
            print("File doesn't exis", file_path)
            return []

        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            soup = BeautifulSoup(file.read(), 'html.parser')

            # collect all releative links to scrape
            releative_links = []
            for link in soup.select('a:not([href^="http"])'):
                releative_links.append(urljoin(file_path, link.get('href')))

            # we use href of up arrow in the navbar to find parent and create hireachy
            up = soup.select_one('body > .spirit-nav > a[accesskey="u"]')
            if up:
                up = urljoin(file_path, up.get('href'))

            heading = soup.select_one('#content > .titlepage, #content > h1:first-child')

            for toc in soup.select('.toc, .copyright, .legalnotice, .author'):
                toc.decompose()

            content = ''
            for sibling in heading.find_next_siblings():
                if sibling.name == 'h2' and sibling.has_attr('id'):
                    break
                content += sibling.get_text().strip() + ' '

            title = sanitize_title(heading.text)
            url = file_path
            lvl0 = [{'title': title, 'url': url}]
            sections[url] = {'lvls': lvl0, 'content': content, 'up': up}

            for subheading in soup.select('#content > h2[id]'):
                content = ''
                for sibling in subheading.find_next_siblings():
                    if sibling.name == 'h2' and sibling.has_attr('id'):
                        break
                    content += sibling.get_text().strip() + ' '

                title = sanitize_title(subheading.text)
                url = file_path + '#' + subheading.get('id')
                lvls = [{'title': title, 'url': url}] + lvl0
                sections[url] = {'lvls': lvls, 'content': content, 'up': up}

            return releative_links

    def _populate_hierachy(self, sections: dict, section: dict):
        if section['up'] not in sections:
            section['up'] = None
            return

        if 'up' in sections[section['up']]:
            self._populate_hierachy(sections, sections[section['up']])

        section['lvls'].extend(sections[section['up']]['lvls'])
        section['up'] = None
