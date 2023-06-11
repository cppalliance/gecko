from bs4 import BeautifulSoup

from .crawler import Crawler

class BoostTokenizer(Crawler):
    '''
    A dedicated crawler for Tokenizer library.
    '''

    def crawl(self, library_key: str) -> dict:
        assert library_key == 'tokenizer'

        doc_path = self._boost_root / 'libs' / library_key / 'doc'

        sections = {}
        for html_file_path in doc_path.glob('*.htm'):
            with open(html_file_path, 'r', encoding='utf-8', errors='ignore') as file:
                soup = BeautifulSoup(file.read(), 'html.parser')

                heading = soup.select_one('body > h1[align=center]')
                if not heading:
                    heading = soup.select_one('body > h1:first-of-type')

                content = ''
                for elm in heading.next_siblings:
                    content += elm.get_text().strip() + ' '

                title = heading.get_text()
                url = str(html_file_path)

                sections[url] = {'lvls': [{'title': title, 'url': url}], 'content': content}

        return sections
