import re
from bs4 import BeautifulSoup

from .crawler import Crawler


def sanitize_title(title):
    return re.sub(r'\s+', ' ', title).strip()


class BoostException(Crawler):
    def crawl(self, library_key: str) -> dict:
        assert library_key == 'exception'

        doc_path = self._boost_root / 'libs' / library_key / 'doc'

        sections = {}
        for html_file_path in doc_path.glob('*.html'):
            with open(html_file_path, 'r', encoding='utf-8', errors='ignore') as file:
                soup = BeautifulSoup(file.read(), 'html.parser')

                heading = soup.select_one('div.body-2 > div.RenoIncludeDIV > div.RenoAutoDIV')
                if not heading:
                    heading = soup.select_one('div.body-2 > div.RenoIncludeDIV > h2')

                content = ''
                for elm in heading.next_siblings:
                    content += elm.get_text().strip() + ' '

                title = sanitize_title(heading.get_text())
                url = str(html_file_path)

                sections[url] = {'lvls': [{'title': title, 'url': url}], 'content': content}

        return sections
