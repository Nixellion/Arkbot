import os
import yaml
from paths import APP_DIR

with open(os.path.join(APP_DIR, 'config', 'config.yaml'), 'r', encoding='utf-8', errors='ignore') as f:
    config = yaml.load(f.read())


class Server(object):
    def __init__(self, config):
        for key, value in config.items():
            self.__dict__[key] = value

server = Server(config)


with open(os.path.join(APP_DIR, 'VERSION'), 'r', encoding='utf-8') as f:
    version = f.read()