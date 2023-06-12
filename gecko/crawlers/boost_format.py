from bs4 import BeautifulSoup

from .crawler import Crawler


class BoostFormat(Crawler):
    def crawl(self, library_key: str) -> dict:
        assert library_key == 'format'

        sections = {}
        html_file_path = self._boost_root / 'libs' / library_key / 'doc/format.html'

        with open(html_file_path, 'r', encoding='utf-8', errors='ignore') as file:
            soup = BeautifulSoup(file.read(), 'html.parser')

            last_h2 = None

            for a in soup.select('body > a[name]'):
                url = str(html_file_path) + '#' + a.get('name')
                content = ''
                lvls = []
                for elm in a.next_elements:
                    if elm.name == 'h2':
                        # meets the next heading
                        if len(lvls) > 0:
                            break
                        lvls = [{'title': elm.get_text(), 'url': url}]
                        last_h2 = lvls
                    elif elm.name == 'h3':
                        # meets the next heading
                        if len(lvls) > 0:
                            break
                        lvls = last_h2 + [{'title': elm.get_text(), 'url': url}]
                    else:
                        content += elm.get_text().strip() + ' '

                sections[url] = {'lvls': lvls, 'content': content}

        return sections
