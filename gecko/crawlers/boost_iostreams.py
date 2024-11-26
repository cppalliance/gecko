import re

from bs4 import BeautifulSoup, Tag
from lxml_html_clean import Cleaner

from .crawler import Crawler


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


class BoostIostreams(Crawler):
    def crawl(self, library_key: str) -> dict:
        assert library_key == 'iostreams'

        doc_path = self._boost_root / 'libs' / library_key / 'doc'

        sections = {}
        for html_file_path in doc_path.rglob('*.html'):
            with open(html_file_path, 'r', encoding='utf-8', errors='ignore') as file:
                # sanitize_html fixes errors in handwritten HTML
                soup = BeautifulSoup(sanitize_html(file.read()), 'html.parser')

                if not soup.select_one('body > .page-index'):
                    continue

                for elm in soup.select('.copyright'):
                    elm.decompose()

                heading = soup.select_one('body > h1.title')
                anchors = [a.get('href') for a in soup.select('body > .page-index a')]

                lvl0 = [{'title': sanitize_title(heading.get_text()), 'path': str(html_file_path)}]

                for a in soup.select('body > a[name]'):
                    if '#' + a.get('name') in anchors:
                        sub_heading = a.find_next_sibling(['h2', 'h3', 'h4'])
                        content = ''
                        for elm in sub_heading.next_siblings:
                            if isinstance(elm, Tag) and elm.has_attr('name') and '#' + elm.get('name') in anchors:
                                break
                            content += elm.get_text().strip() + ' '

                        title = sanitize_title(sub_heading.text)
                        path = str(html_file_path) + '#' + a.get('name')
                        sections[path] = {'lvls': lvl0 + [{'title': title, 'path': path}], 'content': content}

        return sections
