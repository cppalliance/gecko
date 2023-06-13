import re

from bs4 import BeautifulSoup, Tag

from .crawler import Crawler
from .helpers import has_class


def sanitize_title(title):
    return re.sub(r'\s+', ' ', title).strip()


def extract_textblock(textblock: Tag, lvls: list, html_file_path: str, sections: dict):
    main_content = ''
    last_h1_tag = None
    section_content = ''

    def add_sub_section(h1: Tag):
        title = sanitize_title(h1.get_text())
        url = html_file_path + '#' + h1.select_one('a.anchor').get('id')
        sections[url] = {'lvls': lvls + [{'title': title, 'url': url}], 'content': section_content}

    for elm in textblock.children:
        if elm.name == 'h1' and elm.select_one('a.anchor'):
            if last_h1_tag:
                add_sub_section(last_h1_tag)
                section_content = ''
            last_h1_tag = elm
            continue
        if not last_h1_tag:
            main_content += elm.get_text() + ' '
        else:
            section_content += elm.get_text() + ' '

    if last_h1_tag:
        add_sub_section(last_h1_tag)

    return main_content


def extract_memberdecls(memberdecls: Tag, lvls: list, html_file_path: str, sections: dict):
    heading = memberdecls.select_one('tr:first-child > td > h2.groupheader')
    title = sanitize_title(heading.get_text())
    url = html_file_path + '#' + heading.select_one('a[name]').get('name')

    content = ''
    for tr in memberdecls.select('tr'):
        if has_class(tr, 'heading'):
            continue
        content += tr.get_text() + ' '

    content = content.replace('More...', '')
    sections[url] = {'lvls': lvls + [{'title': title, 'url': url}], 'content': content}


def extract_memtitle(memtitle: Tag, lvls: list, html_file_path: str, sections: dict):
    memtitle.select_one('span').decompose()
    title = sanitize_title(memtitle.get_text())
    url = html_file_path + '#' + memtitle.find_previous_sibling('a').get('id')
    content = memtitle.find_next_sibling('div').get_text()
    sections[url] = {'lvls': lvls + [{'title': title, 'url': url}], 'content': content}


class Doxygen(Crawler):
    def crawl(self, library_key: str) -> dict:
        doc_path = self._boost_root / 'libs' / library_key / 'doc/html'

        sections = {}
        for html_file_path in doc_path.glob('*.html'):
            ignored_paths = ['8cpp-example.html', '8hpp.html', 'html/dir_', '_source.html']

            if any(i in str(html_file_path) for i in ignored_paths):
                continue

            with open(html_file_path, 'r', encoding='utf-8', errors='ignore') as file:
                soup = BeautifulSoup(file.read(), 'html.parser')

                wrapper = soup.select_one('div.PageDoc')
                if not wrapper:
                    wrapper = soup.select_one('body')

                if wrapper.select_one('table.classindex, div.directory, table.directory'):
                    continue

                heading = wrapper.select_one('.header > .headertitle > .title')
                if not heading:
                    continue

                lvls = []
                ingroups = heading.select_one('div.ingroups > a')
                if ingroups:
                    lvls = [{'title': sanitize_title(ingroups.text), 'url': str(
                        html_file_path.parent / ingroups.get('href'))}]

                for elm in heading.find_all():
                    elm.decompose()

                title = sanitize_title(heading.get_text())
                url = str(html_file_path)
                lvls += [{'title': title, 'url': url}]

                content = ''
                for elm in wrapper.select_one('.contents').find_all(recursive=False):
                    if has_class(elm, 'textblock'):
                        content += extract_textblock(elm, lvls, str(html_file_path), sections)
                        continue

                    if has_class(elm, 'memberdecls'):
                        extract_memberdecls(elm, lvls, str(html_file_path), sections)
                        continue

                    if has_class(elm, 'memtitle'):
                        extract_memtitle(elm, lvls, str(html_file_path), sections)

                    if has_class(elm, 'memitem'):
                        continue

                    content += elm.get_text() + ' '

                sections[url] = {'lvls': lvls, 'content': content}

        return sections
