"""Extracts search records from documentation in Boost release directory
Usage:
    extract_records
    extract_records --concurrency=4

Options:
  -h --help              Show this screen
  --concurrency=<level>  Concurrency level

"""
from multiprocessing import Pool
from pathlib import Path
import json
import os
import re
from docopt import docopt

from .crawlers import *
from .config import config


def extract_library_name(library_key: str, boost_root: Path):
    libraries_json = boost_root / 'libs' / library_key / 'meta/libraries.json'

    # workaround for tribool
    if library_key == 'tribool':
        libraries_json = boost_root / 'libs' / 'logic' / 'meta/libraries.json'

    # workaround for string_algo path
    if library_key == 'string_algo':
        library_key = 'algorithm/string'

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


def create_algolia_records(library_key: str, sections: dict, boost_root: str):
    boost_root = Path(boost_root).resolve()
    records = []

    library_name = extract_library_name(library_key, boost_root)

    for _, section in sections.items():
        for lvl in section['lvls']:
            lvl['path'] = lvl['path'].replace(str(boost_root) + '/', '')

        records.append({
            'type': 'content',
            'library_key': library_key,
            'library_name': library_name,
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


def extract_records(crawler_name: str, library_key: str, boost_root: Path):
    crawler = globals()[crawler_name](boost_root)
    sections = crawler.crawl(library_key)
    create_algolia_records(library_key, sections, boost_root)


if __name__ == "__main__":
    args = docopt(__doc__)

    concurrency = int(args['--concurrency']) if args['--concurrency'] else None

    with Pool(concurrency) as pool:
        task_args = []
        for crawler_cfg in config['crawlers']:
            for library_cfg in crawler_cfg['libraries']:
                task_args.append((crawler_cfg['name'], library_cfg['key'], config['boost']['root']))

        pool.starmap(extract_records, task_args)
