import os
import yaml
from schema import Schema

config_schema = Schema({
    "boost_version": str,
    "boost_root": os.path.exists,
    "crawlers": [
        {
            "name": str,
            "libraries": [str]
        }
    ]
})

config = {}

with open("./config.yaml", "r", encoding='utf-8') as file:
    config = yaml.safe_load(file)
    config_schema.validate(config)
