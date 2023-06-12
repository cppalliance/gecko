from bs4 import BeautifulSoup

from .crawler import Crawler


class BoostPolygon(Crawler):
    def crawl(self, library_key: str) -> dict:
        assert library_key == 'polygon'

        doc_path = self._boost_root / 'libs' / library_key / 'doc'

        sections = {}
        for html_file_path in doc_path.glob('*.htm'):
            with open(html_file_path, 'r', encoding='utf-8', errors='ignore') as file:
                soup = BeautifulSoup(file.read(), 'html.parser')

                rside = soup.select_one('body > table:first-child > tbody > tr > td:nth-child(2)')
                if not rside:
                    rside = soup.select_one('body')

                heading = rside.select_one('h1')
                if not heading:
                    continue

                content = ''
                for elm in heading.next_siblings:
                    content += elm.get_text().strip() + ' '

                title = heading.get_text()
                url = str(html_file_path)

                sections[url] = {'lvls': [{'title': title, 'url': url}], 'content': content}

        return sections
