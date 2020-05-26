import os
import yaml
from paths import APP_DIR

from debug import get_logger
log = get_logger("arkbot")

with open(os.path.join(APP_DIR, 'config', 'config.yaml'), 'r', encoding='utf-8', errors='ignore') as f:
    config = yaml.load(f.read())


class Server(object):
    def __init__(self, config):
        for key, value in config.items():
            self.__dict__[key] = value

server = Server(config)



with open(os.path.join(APP_DIR, 'VERSION'), 'r', encoding='utf-8') as f:
    version = f.read()


def read_config(name):
    log.debug(f"Reading config {name}")
    fp = os.path.join(APP_DIR, 'config', f"{name}.yaml")
    if not os.path.exists(fp):
        return None
    with open(fp, 'r', encoding='utf-8') as f:
        return yaml.load(f.read())

def write_config(name, data):
    log.debug(f"Writing config {name}")
    with open(os.path.join(APP_DIR, 'config', f"{name}.yaml"), 'w+', encoding='utf-8') as f:
        return f.write(yaml.dump(data), default_flow_style=False)