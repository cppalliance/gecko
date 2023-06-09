import os
import re
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup, Tag

from .crawler import Crawler


def sanitize_title(title):
    title = re.sub(r'\s+', ' ', title).strip()

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


def pop_level(contents, lvl1, sections, titles, urls):
    lvls = [{
        'title': titles[-1]['title'],
        'url': urls[-1]['url']
    }] + ([{'title': titles[-2]['title'], 'url': urls[-2]['url']}] if len(titles) > 1 else lvl1)
    sections[urls[-1]['url']] = {
        'lvls': lvls,
        'content': '\n'.join(contents[-1]),
        'up': urls[-2]['url'] if len(urls) > 1 else lvl1[0]['url']
    }
    urls.pop()
    titles.pop()
    contents.pop()


def push_level(child, file_path, titles, urls, contents):
    new_title = sanitize_title(child.get_text("\n"))
    new_url = file_path + '#' + child.select_one('a').get('id')
    urls.append({
        'level': child.name,
        'url': new_url
    })
    titles.append({
        'level': child.name,
        'title': new_title
    })
    contents.append([])


def crawl_index_page(file_path, soup, sections):
    title = sanitize_title(
        soup.select_one('body > #doc-content > .PageDoc > .header > .headertitle > .title').get_text("\n"))
    content = soup.select_one('body > #doc-content > .PageDoc > .contents > .textblock')
    urls = []
    titles = []
    contents = []

    lvl1 = [{
        'title': title,
        'url': file_path
    }]

    for child in content:
        if isinstance(child, Tag):
            if not child.select_one('a') or not child.select_one('a').get('id'):
                contents[-1] += [child.get_text("\n")]
            else:
                if not urls or child.name > urls[-1]['level']:
                    push_level(child, file_path, titles, urls, contents)
                else:
                    while urls and child.name <= urls[-1]['level']:
                        pop_level(contents, lvl1, sections, titles, urls)
                    push_level(child, file_path, titles, urls, contents)
    while urls:
        pop_level(contents, lvl1, sections, titles, urls)


def is_directory(child):
    return child.select_one('span.iconfopen') or child.select_one('span.iconfclose')


def create_file_hierarchy(file_path: str) -> dict:
    parents = {}
    file_hierarchy = {}
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        soup = BeautifulSoup(file.read(), 'html.parser')

        directory = soup.select_one('table.directory')
        for child in directory.children:
            if isinstance(child, Tag):
                url = urljoin(file_path, child.select_one('td > a').get('href'))
                levels = tuple(int(level) for level in child['id'].replace('row_', '').split('_')[1:-1])
                if is_directory(child):
                    parents[levels] = url
                if levels[:-1]:
                    file_hierarchy[url] = parents[levels[:-1]]
                else:
                    file_hierarchy[url] = file_path

    return file_hierarchy


def crawl_reference_page(contents, file_path, sections, title, up):
    lvl1 = [{
        'title': title,
        'url': file_path
    }]
    if title in ['Concepts', 'Data types', 'Functional', 'Core',
                 'Experimental features', 'External adapters',
                 'Configuration options',
                 'Assertions', 'Details']:
        lvl1 += [{'title': 'Reference documentation', 'url': urljoin(file_path, 'modules.html')}]
    copyright_notice = contents.select_one('.copyright')
    if copyright_notice:
        copyright_notice.decompose()
    content = []
    anchors = []
    anchor_found = False
    for child in contents.children:
        if isinstance(child, Tag):
            if child.name == 'a' and child.has_attr('id'):
                child_id = child.get('id')
                anchors.append({'id': child_id})
                anchor_found = True
            elif child.name == 'table' and child.select_one('.heading'):
                heading, *body = child.select('tr')
                link = heading.select_one('a').get('name')
                section_title = sanitize_title(heading.get_text("\n"))
                section_body = '\n'.join([x.get_text("\n") for x in body])
                if section_body.find('More...') != -1:
                    continue
                url = file_path + '#' + link
                sections[url] = {
                    'content': section_body,
                    'lvls': [{
                        'title': section_title,
                        'url': url
                    }] + lvl1,
                    'up': up
                }
            elif anchor_found:
                if child.name in ['h2', 'h3', 'h4', 'h5', 'h6']:
                    anchors[-1]['title'] = sanitize_title(child.find(text=True, recursive=False))
                    continue
                memproto = child.select_one('.memproto')
                if memproto:
                    if 'title' not in anchors[-1]:
                        anchors[-1]['title'] = sanitize_title(memproto.get_text("\n"))
                    doc = child.select_one('.memdoc')
                    anchors[-1]['doc'] = doc.get_text("\n")
                else:
                    anchors[-1]['doc'] = child.get_text("\n")
                anchor_found = False
            elif child.name not in ['h2', 'h3', 'h4', 'h5', 'h6']:
                content.append(child.get_text("\n"))
    # merge all content
    content = '\n'.join(content)
    if content.find('More...') == -1:
        sections[file_path] = {
            'lvls': lvl1,
            'content': content,
            'up': up,
        }
    for anchor in anchors:
        lvl2 = [{
            'title': anchor['title'],
            'url': file_path + '#' + anchor['id'],
        }]
        sections[file_path + '#' + anchor['id']] = {
            'lvls': lvl2 + lvl1,
            'content': anchor['doc'],
            'up': up,
        }


def scrape_html_file(file_path: str, sections: dict, file_hierarchy: dict) -> set:
    if not os.path.isfile(file_path):
        print("File doesn't exist", file_path)
        return set()

    # skip functions.html
    if file_path.endswith('functions.html'):
        return set()

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        soup = BeautifulSoup(file.read(), 'html.parser')

        # collect all relative links to return for scrape
        releative_links = set()
        for link in soup.select('a:not([href^="http"])'):
            releative_links.add(urljoin(file_path, link.get('href')))

        if os.path.basename(file_path) == 'index.html':
            crawl_index_page(file_path, soup, sections)
            return releative_links

        links = soup.select('body > #doc-content > .header > .headertitle > .title > .ingroups > .el')
        if links:
            up = urljoin(file_path, links[-1].get('href'))
        elif file_path in file_hierarchy:
            up = file_hierarchy[file_path]
        elif up := soup.select_one('body > #doc-content > .contents > p > a.el') or soup.select_one(
                'body > #doc-content > .contents > .textblock > p > code > a.el'):
            up = urljoin(file_path, up.get('href'))

        title = soup.select_one('.header > .headertitle > .title')
        if title:
            title = sanitize_title(title.find(text=True, recursive=False))

            contents = soup.select_one('body > #doc-content > .contents') or soup.select_one(
                'body > #doc-content > .PageDoc > .contents')
            if not contents:
                return releative_links

            crawl_reference_page(contents, file_path, sections, title, up)
        return releative_links


class Hana(Crawler):
    def crawl(self, _) -> dict:
        sections = {}
        index_path = self._boost_root / 'libs' / 'hana' / 'index.html'

        # resolve redirect address
        with open(index_path, 'r', encoding='utf-8', errors='ignore') as file:
            soup = BeautifulSoup(file.read(), 'html.parser')
            assert soup.select_one('head > meta[http-equiv="refresh"]')
            redirect_to = soup.select_one('body a').get("href")
            redirect_to = redirect_to.replace('https://www.boost.org/doc/libs/master/', '../../')
            index_path = urljoin(str(index_path), redirect_to)

        links_to_scrape = {index_path,
                           *(urljoin(index_path, file) for file in ['modules.html', 'todo.html'])}
        scraped_links = set()
        file_hierarchy = create_file_hierarchy(urljoin(index_path, 'files.html'))

        while len(links_to_scrape) > 0:
            link = links_to_scrape.pop()
            scraped_links.add(link)

            releative_links = scrape_html_file(file_path=link, sections=sections, file_hierarchy=file_hierarchy)

            for link in releative_links:
                # remove anchor
                link = urlparse(link).path

                if not link.endswith(".html"):
                    continue

                if 'hana' not in link.lower():
                    continue

                if link not in scraped_links:
                    links_to_scrape.add(link)

        for _, section in sections.items():
            self._populate_hierarchy(sections, section)

        for _, section in sections.items():
            section['lvls'] = remove_duplicate_lvls(section['lvls'])

            section['lvls'].reverse()

        return sections

    def _populate_hierarchy(self, sections: dict, section: dict):
        if section['up'] not in sections:
            section['up'] = None
            return

        if 'up' in sections[section['up']]:
            self._populate_hierarchy(sections, sections[section['up']])

        section['lvls'].extend(sections[section['up']]['lvls'])
        section['up'] = None
