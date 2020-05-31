'''
Lock system, can create, check and manage file locks.
Can be used with, for example, cron job scripts to check if another script is already running, or
for whatever you can think of.
'''


import os
from paths import APP_DIR

from debug import get_logger
log = get_logger("arkbot")

class Lock(object):
    def __init__(self, name="general"):
        self.name = name
        self.filepath = os.path.join(APP_DIR, f"{name}.lock")

    @property
    def locked(self):
        return os.path.exists(self.filepath)

    is_locked = locked

    @property
    def message(self):
        if self.locked:
            with open(self.filepath, "r") as f:
                return f.read()
        else:
            log.warning(f"Lock {self.name} does not exist.")

    @message.setter
    def message(self, value):
        if self.locked:
            with open(self.filepath, "w") as f:
                f.write(value)
        else:
            log.warning(f"Lock {self.name} does not exist.")

    def lock(self, message=""):
        log.debug(f"Locking {self.name}...")
        with open(self.filepath, "w+") as f:
            f.write(message)

    def unlock(self):
        log.debug(f"Unlocking {self.name}...")
        if self.locked:
            os.remove(self.filepath)
        else:
            log.debug(f"Lock {self.name} is already unlocked.")



def get_locks():
    locks = []
    for filename in os.listdir(APP_DIR):
        name, ext = os.path.splitext(filename)
        if ext == ".lock":
            locks.append(Lock(name))
    return locks