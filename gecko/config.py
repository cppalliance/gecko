import os
from ruamel.yaml import YAML
from schema import Schema

config_schema = Schema({
    'boost': {
        'version': str,
        'root': os.path.exists,
        'link': str,
    },
    'website-v2-docs': {
        'root': os.path.exists,
        'sections': [
            {
                'key': str,
                'name': str,
                'last-records': int,
                'last-words': int,
                'last-lvls': int
            }
        ]
    },
    'algolia': {
        'app-id': str,
        'api-key': str,
        'settings': dict
    },
    'crawlers': [
        {
            'name': str,
            'libraries': [
                {
                    'key': str,
                    'last-records': int,
                    'last-words': int,
                    'last-lvls': int
                }
            ]
        }
    ]
})

config = {}

config_path = './config/config.local.yaml'

# try to load local config if exists
if not os.path.exists(config_path):
    config_path = './config/config.yaml'

with open(config_path, 'r', encoding='utf-8') as file:
    yaml = YAML()
    yaml.preserve_quotes = True
    config = yaml.load(file)
    config_schema.validate(config)


def update_config_file():
    with open(config_path, 'w', encoding='utf-8') as file:
        yaml = YAML()
        yaml.indent(mapping=2, sequence=4, offset=2)
        yaml.dump(config, file)
