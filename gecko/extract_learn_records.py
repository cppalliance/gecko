import re
import json
from pathlib import Path
from urllib.parse import urljoin
from bs4 import BeautifulSoup, Tag

from .crawlers.helpers import has_class
from .config import config


class AntoraDoc():
    def crawl(self, doc_root: Path) -> dict:
        sections = {}
        doc_root = doc_root.resolve()

        for file_path in doc_root.rglob('*.html'):
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                soup = BeautifulSoup(file.read(), 'html.parser')

                lvls = []
                for link in soup.select('body nav.breadcrumbs ul li a'):
                    lvls = lvls + [{'title': link.text, 'path': urljoin(str(file_path), link.get('href'))}]

                sect1 = soup.select_one('body article.doc')
                if sect1:
                    self._extract_section_n(str(file_path), sections, sect1, lvls)

        return sections

    def _extract_section_n(self, file_path: str, sections: dict, sect: Tag, lvls: list = []):
        header = sect.select_one('h1, h2, h3, h4, h5, h6')

        if header.name == 'h1':
            path = file_path
        else:
            title = header.text
            path = file_path + '#' + header.get('id')
            lvls = lvls + [{'title': title, 'path': path}]

        if header.find_next_sibling() and has_class(header.find_next_sibling(), 'sectionbody'):
            siblings = header.find_next_sibling().find_all(recursive=False)
        else:
            siblings = header.next_siblings

        content = ''
        for sibling in siblings:
            if isinstance(sibling, Tag) and sibling.has_attr('class') and len([i for i in sibling.get('class') if i.startswith('sect')]) > 0:
                self._extract_section_n(file_path, sections, sibling, lvls)
                continue
            content += sibling.get_text() + ' '

        sections[path] = {'content': content, 'lvls': lvls}


def create_algolia_records(section_key: str, section_name: str, doc_root: Path, sections: dict):
    doc_root = doc_root.resolve()
    records = []

    for _, section in sections.items():
        for lvl in section['lvls']:
            lvl['path'] = lvl['path'].replace(str(doc_root) + '/', '')

        records.append({
            'type': 'content',
            'section_key': section_key,
            'section_name': section_name,
            'content': re.sub(r'\s+', ' ', section['content']).strip(),
            'weight': {
                'pageRank': 0,
                'level': 100 - len(section['lvls']) * 10,
                'position': 0
            },
            'path': section['lvls'][-1]['path'] if len(section['lvls']) > 0 else None,
            'hierarchy': {
                'lvl0': section['lvls'][0] if len(section['lvls']) > 0 else None,
                'lvl1': section['lvls'][1] if len(section['lvls']) > 1 else None,
                'lvl2': section['lvls'][2] if len(section['lvls']) > 2 else None,
                'lvl3': section['lvls'][3] if len(section['lvls']) > 3 else None,
                'lvl4': section['lvls'][4] if len(section['lvls']) > 4 else None,
                'lvl5': section['lvls'][5] if len(section['lvls']) > 5 else None,
                'lvl6': section['lvls'][6] if len(section['lvls']) > 6 else None
            }})

    with open('./algolia_records/learn/' + section_key + '.json', 'w', encoding='utf-8') as outfile:
        json.dump(records, outfile, indent=4)


if __name__ == "__main__":
    crawler = AntoraDoc()

    for section in config['website-v2-docs']['sections']:
        sections = crawler.crawl(Path(config['website-v2-docs']['root']) / section['key'])
        create_algolia_records(section['key'],
                               section['name'],
                               Path(config['website-v2-docs']['root']),
                               sections)
