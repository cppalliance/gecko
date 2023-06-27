"""Checks the sanity of generated Algolia records
Usage:
    sanitizer check
    sanitizer update-config
    sanitizer -h
"""
import re
import json
import sys
from pathlib import Path
from docopt import docopt

from .config import config, update_config_file


def check_for_abnormality(nbof: str, library_key: str, prev: int, curr: int):
    if (abs(curr - prev) / prev) > 0.2:
        print('Error: Abnormal change in number of {} in {} from:{} to:{}'.format(nbof, library_key, prev,  curr))
        return True
    return False


if __name__ == "__main__":
    args = docopt(__doc__)

    if args['check']:
        failed = False
        for crawler_cfg in config['crawlers']:
            for library_cfg in crawler_cfg['libraries']:
                json_file_path = Path('./algolia_records') / f"{library_cfg['key'].replace('/','_')}.json"
                with open(json_file_path, 'r', encoding='utf-8') as f:
                    records = json.load(f)
                    words = 0
                    lvls = 0
                    for record in records:
                        words += len(re.findall(r'\w+', record['content']))
                        lvls += len([l for l in record['hierarchy'].values() if l is not None])

                    failed |= check_for_abnormality(
                        nbof='records',
                        library_key=library_cfg['key'],
                        prev=library_cfg['last-records'],
                        curr=len(records))

                    failed |= check_for_abnormality(
                        nbof='words',
                        library_key=library_cfg['key'],
                        prev=library_cfg['last-words'],
                        curr=words)

                    failed |= check_for_abnormality(
                        nbof='lvls',
                        library_key=library_cfg['key'],
                        prev=library_cfg['last-lvls'],
                        curr=lvls)

        if failed:
            sys.exit(1)

    if args['update-config']:
        for crawler_cfg in config['crawlers']:
            for library_cfg in crawler_cfg['libraries']:
                json_file_path = Path('./algolia_records') / f"{library_cfg['key'].replace('/','_')}.json"
                with open(json_file_path, 'r', encoding='utf-8') as f:
                    records = json.load(f)
                    library_cfg['last-records'] = len(records)
                    library_cfg['last-words'] = 0
                    library_cfg['last-lvls'] = 0
                    for record in records:
                        library_cfg['last-words'] += len(re.findall(r'\w+', record['content']))
                        library_cfg['last-lvls'] += len([l for l in record['hierarchy'].values() if l is not None])

        update_config_file()
        print('Config has been updated.')
