from pathlib import Path
import re
import json
import os

from .crawlers import *
from .config import config


def extract_library_name(library_key: str, boost_root: Path):
    libraries_json = boost_root / 'libs' / library_key / 'meta/libraries.json'

    # workaround for tribool
    if library_key == 'tribool':
        libraries_json = boost_root / 'libs' / 'logic' / 'meta/libraries.json'

    # use parent directory for boost.functional
    if not os.path.isfile(libraries_json):
        libraries_json = boost_root / 'libs' / library_key.split('/')[0] / 'meta/libraries.json'

    with open(libraries_json, 'r', encoding='utf-8') as file:
        meta = json.load(file)
        if isinstance(meta, list):
            library_name = [m for m in meta if m['key'] == library_key][0]['name']
        else:
            library_name = meta['name']

    return library_name


def create_algolia_records(library_key: str, sections: dict, boost_root: str, boost_version: str):
    boost_root = Path(boost_root).resolve()
    records = []

    library_name = extract_library_name(library_key, boost_root)

    for _, section in sections.items():
        for lvl in section['lvls']:
            lvl['url'] = lvl['url'].replace(str(boost_root), 'https://www.boost.org/doc/libs/' + boost_version)

        records.append({
            'type': 'content',
            'library_key': library_key,
            'library_name': library_name,
            'boost_version': boost_version,
            'content': re.sub(r'\s+', ' ', section['content']).strip(),
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

    with open('./algolia_records/' + library_key.replace('/', '_') + '.json', 'w', encoding='utf-8') as outfile:
        json.dump(records, outfile, indent=4)


if __name__ == "__main__":

    for crawler_cfg in config['crawlers']:
        crawler = globals()[crawler_cfg['name']](boost_root=config['boost_root'])

        for library_key in crawler_cfg['libraries']:
            sections = crawler.crawl(library_key)

            create_algolia_records(library_key=library_key,
                                   sections=sections,
                                   boost_root=config['boost_root'],
                                   boost_version=config['boost_version'])
