import os
import re
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from .crawler import Crawler
from .helpers import has_class


def sanitize_title(title):
    title = re.sub(r'\s+', ' ', title).strip()

    # Workaround for Reference page in Boost.Beast
    if 'This Page Intentionally Left Blank' in title:
        return 'Reference'

    title = title.replace('¶', '')

    return title


def remove_duplicate_lvls(lvls: list):
    encountered_titles = set()
    unique_dicts = []

    for lvl in lvls:
        title = lvl['title']
        if title not in encountered_titles:
            unique_dicts.append(lvl)
            encountered_titles.add(title)

    return unique_dicts


class QuickBook(Crawler):
    def crawl(self, library_key: str) -> dict:
        sections = {}
        index_path = self._boost_root / 'libs' / library_key / 'index.html'

        # workaround for tribool path
        if library_key == 'tribool':
            index_path = self._boost_root / 'libs' / 'logic' / 'index.html'

        # resolve redirect address
        with open(index_path, 'r', encoding='utf-8', errors='ignore') as file:
            soup = BeautifulSoup(file.read(), 'html.parser')
            assert soup.select_one('head > meta[http-equiv="refresh"]')
            redirect_to = soup.select_one('body a').get("href")
            # workaround for libraries not utilizing relative urls
            redirect_to = redirect_to.replace('https://www.boost.org/doc/libs/master/', '../../')
            index_path = urljoin(str(index_path), redirect_to)

        links_to_scrape = set([index_path])
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
            section['lvls'] = remove_duplicate_lvls(section['lvls'])

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

            # remove index sections from pages, like:
            # https://www.boost.org/doc/libs/1_82_0/doc/html/boost_asio/index.html
            for index in soup.select('.section .index'):
                if index.find_parent(class_='section'):
                    index.find_parent(class_='section').decompose()

            # collect all releative links to scrape
            releative_links = []
            for link in soup.select('a:not([href^="http"])'):
                releative_links.append(urljoin(file_path, link.get('href')))

            # we use href of up arrow in the navbar to find parent and create hireachy
            # navfooter is used in msm library
            up = soup.select_one('body > .spirit-nav > a[accesskey="u"], body > .navfooter a[accesskey="u"]')
            if up and up.get('href') != '#':
                up = urljoin(file_path, up.get('href'))

            # ref pages have a different structure, like:
            # https://www.boost.org/doc/libs/1_82_0/doc/html/boost/algorithm/erase_range_copy.html
            if soup.select_one('body > .refentry'):
                lvl1 = [{
                    'title': sanitize_title(soup.select_one('.refentry > .refnamediv > h2').text),
                    'url': file_path
                }]

                for refsect1 in soup.select('.refentry > .refsect1'):
                    anchor = refsect1.select_one('a').get('name')

                    content = ''
                    for sibling in refsect1.select_one('h2').find_next_siblings():
                        if has_class(sibling, 'refsect2'):
                            break
                        content += sibling.get_text().strip() + ' '

                    url = file_path + '#' + anchor
                    lvl2 = [{
                        'title': sanitize_title(refsect1.select_one('h2').text),
                        'url': url
                    }]+lvl1

                    sections[url] = {'lvls': lvl2, 'content': content, 'up': up}

                    for refsect2 in refsect1.select('.refsect2'):
                        anchor = refsect2.select_one('a').get('name')

                        content = ''
                        for sibling in refsect2.select_one('h3').find_next_siblings():
                            if has_class(sibling, 'refsect3'):
                                break
                            content += sibling.get_text().strip() + ' '

                        url = file_path + '#' + anchor
                        lvl3 = [{
                            'title': sanitize_title(refsect2.select_one('h3').text),
                            'url': url
                        }]+lvl2
                        sections[url] = {'lvls': lvl3, 'content': content, 'up': up}
            else:
                for anchor in soup.select('h1 > a.headerlink, h2 > a.headerlink, h3 > a.headerlink, h4 > a.headerlink, '
                                          'h5 > a.headerlink, h6 > a.headerlink, h1 > a.link, h2 > a.link, h3 > a.link,'
                                          'h4 > a.link, h5 > a.link, h6 > a.link, h1.title > a:first-child, h2.title > '
                                          'a:first-child, h3.title > a:first-child, h4.title > a:first-child, h5.title '
                                          '> a:first-child, h6.title > a:first-child'):
                    # titlepage headers
                    header = anchor.find_parent(class_='titlepage')

                    # regular headers
                    if not header:
                        header = anchor.parent
                        if header.name not in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                            continue

                    content = ''
                    for sibling in header.find_next_siblings():
                        if sibling.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                            break

                        if has_class(sibling, 'section'):
                            break

                        if has_class(sibling, 'toc'):
                            continue

                        content += sibling.get_text().strip() + ' '

                    if anchor.has_attr('href') and header != soup.select_one('.body > .section:first-child > h1'):
                        url = urljoin(file_path, anchor.get('href'))
                    elif header != soup.select_one('body > div > .titlepage') and header != soup.select_one('.body > .section:first-child > h1'):
                        url = file_path + '#' + anchor.get('name')
                    else:
                        url = file_path

                    if soup.select_one('body > div > .titlepage .title'):
                        lvls = [
                            {
                                'title': sanitize_title(anchor.parent.text),
                                'url': url
                            },
                            {
                                'title': sanitize_title(soup.select_one('body > div > .titlepage .title').text),
                                'url': file_path
                            }
                        ]
                    elif soup.select_one('.body > .section:first-child > h1'):
                        lvls = [
                            {
                                'title': sanitize_title(anchor.parent.text),
                                'url': url
                            },
                            {
                                'title': sanitize_title(soup.select_one('.body > .section:first-child > h1').text),
                                'url': file_path
                            }
                        ]
                    else:
                        lvls = [
                            {
                                'title': sanitize_title(anchor.parent.text),
                                'url': url
                            }
                        ]

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
