import re
from bs4 import BeautifulSoup

from lxml.html.clean import Cleaner

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


class BoostGraph(Crawler):
    def crawl(self, library_key: str) -> dict:
        assert library_key == 'graph'

        doc_path = self._boost_root / 'libs' / library_key / 'doc'

        sections = {}
        for html_file_path in doc_path.glob('*.html'):
            with open(html_file_path, 'rb') as file:
                soup = BeautifulSoup(sanitize_html(file.read()), 'html.parser')

                heading = soup.select_one('body > h1:first-of-type,body > h2:first-of-type')
                if not heading:
                    continue

                content = ''
                for elm in heading.next_siblings:
                    if 'Copyright' in elm.text:
                        break
                    content += elm.get_text().strip() + ' '

                title = sanitize_title(heading.get_text())
                path = str(html_file_path)

                sections[path] = {'lvls': [{'title': title, 'path': path}], 'content': content}

        return sections
