import json
import os
import glob
from algoliasearch.search_client import SearchClient

if __name__ == "__main__":
    client = SearchClient.create('D7O1MLLTAF', 'YourWriteAPIKey')
    index = client.init_index("libraries")

    for filename in glob.glob('./records/*.json'):
        print('uploading records for {}.'.format(filename))

        with open(os.path.join(os.getcwd(), filename), 'r') as f:
            records = json.load(f)

            for record in records:
                # TODO do something about truncation of long contents
                record['content'] = record['content'][:90000]

            # TODO instead of using autoGenerateObjectIDIfNotExist we might create a hash out of hierarchy items
            index.save_objects(records, {'autoGenerateObjectIDIfNotExist': True})
