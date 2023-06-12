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

config_path = "./config/config.local.yaml"

# try to load local config if exists
if not os.path.exists(config_path):
    config_path = "./config/config.yaml"

with open(config_path, "r", encoding='utf-8') as file:
    config = yaml.safe_load(file)
    config_schema.validate(config)
