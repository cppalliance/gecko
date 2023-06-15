import re

from bs4 import BeautifulSoup

from .crawler import Crawler


def sanitize_title(title):
    return re.sub(r'\s+', ' ', title).strip()


class BoostPreprocessor(Crawler):
    def crawl(self, library_key: str) -> dict:
        assert library_key == 'preprocessor'

        doc_path = self._boost_root / 'libs' / library_key / 'doc'

        sections = {}
        for html_file_path in doc_path.rglob('*.html'):
            if 'doc/index.html' in str(html_file_path):
                continue

            with open(html_file_path, 'r', encoding='utf-8', errors='ignore') as file:
                soup = BeautifulSoup(file.read(), 'html.parser')

                heading = soup.select_one('body > h4:first-child')
                if not heading:
                    heading = soup.select_one('head > title')
                    title = sanitize_title(heading.get_text())
                    path = str(html_file_path)
                    sections[path] = {'lvls': [{'title': title, 'path': path}], 'content': soup.select_one('body').text}
                    continue

                if '[back]' in heading.text:
                    continue

                content = ''
                for elm in heading.next_siblings:
                    content += elm.get_text().strip() + ' '

                title = sanitize_title(heading.get_text())
                path = str(html_file_path)

                sections[path] = {'lvls': [{'title': title, 'path': path}], 'content': content}

        return sections
