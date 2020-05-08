import time
from random import choice
from ark_manager import *

from locks import Lock

from debug import get_logger

from functools import partial

log = get_logger("arkbot")

import argparse

parser = argparse.ArgumentParser(description='Restart ark server.')
parser.add_argument("--message", dest='message', default=None,
                    help="Message to add to broadcast, usually reason for restart.")
args = parser.parse_args()

if args.message:
    args.message = args.message.strip()
    if not args.message.endswith("."):
        args.message = args.message + ". "
    else:
        args.message = args.message + " "


def mod_updater():
    lock = Lock()

    if lock.locked:
        log.debug("Another script already running, exit...")
        sys.exit()
    modids = check_mod_versions()
    if modids:
        log.info("New mod version found, performing update.")
        lock.lock("Locked for update...")
        delay_with_notifications(message="Updating mods.")
        stop_server()
        log.info(f"Updating mods: {modids}")
        update_mods(modids)
        fix_mods_permissions()
        start_server()
        time.sleep(10 * 60)
        lock.unlock()
    else:
        log.info("No new mod version found.")






if __name__ == "__main__":
    mod_updater()

