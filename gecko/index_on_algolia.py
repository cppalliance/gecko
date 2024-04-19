import json
from pathlib import Path

from algoliasearch.search_client import SearchClient

from .config import config

if __name__ == "__main__":
    client = SearchClient.create(config['algolia']['app-id'], config['algolia']['api-key'])

    print('Initializing {} index ...'.format(config['boost']['version']))
    index = client.init_index(config['boost']['version'])

    print('Setting settings for {} index ...'.format(config['boost']['version']))
    index.set_settings(config['algolia']['settings'])

    for path in Path('./algolia_records').glob('*.json'):
        print('uploading records for {}...'.format(path.stem))

        with open(path, 'r', encoding='utf-8') as f:
            records = json.load(f)

            # Delete the existing records for this library.
            index.delete_by({'filters': 'library_key:{}'.format(records[0]['library_key'])})

            # Split long documents into smaller parts.
            for record in records:
                if len(record['content']) > 5000:
                    new_record = record
                    new_record['content'] = new_record['content'][4900:]
                    record['content'] = record['content'][:5000]
                    records.append(new_record)

            records = [record for record in records if not (
                record['content'] == '' and not record['hierarchy']['lvl0'])]

            # TODO instead of using autoGenerateObjectIDIfNotExist we might create a hash out of hierarchy items
            index.save_objects(records, {'autoGenerateObjectIDIfNotExist': True})
