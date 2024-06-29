import json
from pathlib import Path

from algoliasearch.search_client import SearchClient

from .config import config

if __name__ == "__main__":
    client = SearchClient.create(config['algolia']['app-id'], config['algolia']['api-key'])

    print('Initializing {} index ...'.format(config['boost']['version']))
    libraries_index = client.init_index(config['boost']['version'])

    print('Setting settings for {} index ...'.format(config['boost']['version']))
    libraries_index.set_settings(config['algolia']['settings'])

    for path in Path('./algolia_records/libraries').glob('*.json'):
        print('uploading records for {}...'.format(path.stem))

        with open(path, 'r', encoding='utf-8') as f:
            records = json.load(f)

            # Delete the existing records for this library.
            libraries_index.delete_by({'filters': 'library_key:{}'.format(records[0]['library_key'])})

            # Split long documents into smaller parts.
            for record in records:
                if len(record['content']) > 5000:
                    new_record = record
                    new_record['content'] = new_record['content'][4900:]
                    record['content'] = record['content'][:5000]
                    records.append(new_record)

            records = [record for record in records if not (
                record['content'] == '' and not record['hierarchy']['lvl0'])]

            libraries_index.save_objects(records, {'autoGenerateObjectIDIfNotExist': True})

    learn_index = client.init_index('learn')

    # No need to set settings for the learn index as it is fixed and preconfigured.

    for path in Path('./algolia_records/learn').glob('*.json'):
        print('uploading records for {}...'.format(path.stem))

        with open(path, 'r', encoding='utf-8') as f:
            records = json.load(f)

            # Delete the existing records for this section.
            learn_index.delete_by({'filters': 'section_key:{}'.format(records[0]['section_key'])})

            learn_index.save_objects(records, {'autoGenerateObjectIDIfNotExist': True})
