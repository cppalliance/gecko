import re

from bs4 import BeautifulSoup

from .crawler import Crawler


def sanitize_title(title):
    return re.sub(r'\s+', ' ', title).strip()


class Gargoyle(Crawler):
    def crawl(self, library_key: str) -> dict:
        assert library_key == 'wave' or library_key == 'spirit/classic'

        doc_path = self._boost_root / 'libs' / library_key / 'doc'

        sections = {}
        for html_file_path in doc_path.glob('*.html'):
            with open(html_file_path, 'r', encoding='utf-8', errors='ignore') as file:
                soup = BeautifulSoup(file.read(), 'html.parser')

                heading = soup.select_one('body > table:first-child')

                for elm in soup.select('.copyright, .updated'):
                    elm.decompose()

                content = ''
                for elm in heading.next_siblings:
                    content += elm.get_text().strip() + ' '

                title = sanitize_title(heading.get_text())
                path = str(html_file_path)

                sections[path] = {'lvls': [{'title': title, 'path': path}], 'content': content}

        return sections
