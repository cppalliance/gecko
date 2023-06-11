import re

from bs4 import BeautifulSoup

from .crawler import Crawler


def sanitize_title(title):
    return re.sub(r'\s+', ' ', title).strip()


class BoostFunctional(Crawler):
    '''
    A dedicated crawler for Functional library.
    '''

    def crawl(self, library_key: str) -> dict:
        assert library_key == 'functional'

        sections = {}
        doc_path = self._boost_root / 'libs' / library_key

        for html_file_path in doc_path.glob('*.html'):

            with open(html_file_path, 'r', encoding='utf-8', errors='ignore') as file:
                soup = BeautifulSoup(file.read(), 'html.parser')

                heading = soup.select_one('body > h1')

                lvls = [{'title': sanitize_title(heading.text), 'url': str(html_file_path)}]

                content = ''
                for elm in heading.next_siblings:
                    content += elm.get_text().strip() + ' '

                sections[str(html_file_path)] = {'lvls': lvls, 'content': content}

        return sections
