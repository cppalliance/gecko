import re
import json
import os
from bs4 import BeautifulSoup, Tag
from urllib.parse import urljoin


def extract_section_n(file_path: str, sections: dict, sect: Tag, lvls: list = []):
    hn = sect.select_one('h2, h3, h4, h5, h6')
    lvls = lvls + [hn.text]

    if hn.find_next_sibling() and hn.find_next_sibling().has_attr('class') and 'sectionbody' in hn.find_next_sibling().get('class'):
        siblings = hn.find_next_sibling().find_all(recursive=False)
    else:
        siblings = hn.find_next_siblings()

    content = ''
    for sibling in siblings:
        if sibling.has_attr('class') and len([i for i in sibling.get('class') if i.startswith('sect')]):
            extract_section_n(file_path, sections, sibling, lvls)
            continue
        content += sibling.get_text() + ' '

    sections[file_path + '#' + hn.get('id')] = {'content': content, 'lvls': lvls}


def scrape_html_file(file_path: str, sections: dict):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        soup = BeautifulSoup(file.read(), 'html.parser')

        if soup.select_one('head > meta[http-equiv="refresh"]'):
            redirect_to = soup.select_one('body a').get("href")
            redirect_to = redirect_to.replace('https://www.boost.org/doc/libs/master/', '../../')
            return scrape_html_file(urljoin(file_path, redirect_to), sections)

        for sect1 in soup.select('body > div[id="content"] > .sect1'):
            extract_section_n(file_path, sections, sect1)


def create_algolia_records(library: str, sections: dict, boost_root_path: str, boost_version: str):
    records = []
    for url, section in sections.items():
        url = url.replace(boost_root_path, 'https://www.boost.org/doc/libs/' + boost_version)

        records.append({
            'type': 'content',
            'library': library,
            'boost_version': boost_version,
            'url': url,
            'content': re.sub('\s+', ' ', section['content']).strip(),
            'weight': {
                'pageRank': 0,
                'level': 100 - len(section['lvls']) * 10,
                'position': 0
            },
            'hierarchy': {
                'lvl0': section['lvls'][0] if len(section['lvls']) > 0 else None,
                'lvl1': section['lvls'][1] if len(section['lvls']) > 1 else None,
                'lvl2': section['lvls'][2] if len(section['lvls']) > 2 else None,
                'lvl3': section['lvls'][3] if len(section['lvls']) > 3 else None,
                'lvl4': section['lvls'][4] if len(section['lvls']) > 4 else None,
                'lvl5': section['lvls'][5] if len(section['lvls']) > 5 else None,
                'lvl6': section['lvls'][6] if len(section['lvls']) > 6 else None
            }})

    with open('./records/' + library + '.json', 'w') as outfile:
        json.dump(records, outfile, indent=4)


if __name__ == "__main__":
    libraries = ['describe', 'leaf', 'endian', 'variant2', 'container_hash', 'system', 'predef', 'qvm', 'unordered', 'smart_ptr', 'lambda2', 'assert', 'io', 'throw_exception', 'mp11']

    boost_root_path = '../boost_1_82_0'
    boost_root_path = os.path.abspath(boost_root_path)

    for library in libraries:
        file_path = boost_root_path + '/libs/' + library + '/index.html'

        sections = {}
        scrape_html_file(file_path=file_path, sections=sections)

        create_algolia_records(library=library,
                               sections=sections,
                               boost_root_path=boost_root_path,
                               boost_version='1_82_0')
