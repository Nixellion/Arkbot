import time
from random import choice
from ark_manager import *

from locks import Lock

from debug import get_logger

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
    modids = check_mod_versions()
    if modids:
        log.info("New mods detected.")
        stop_server()
        log.info(f"Updating mods: {modids}")
        update_mods(modids)
        fix_mods_permissions()
        start_server()
        time.sleep(10 * 60)


if __name__ == "__main__":
    run_with_lock(run_with_delay(mod_updater, delay_minutes=[15, 10, 5], message="Updating mods"), "Mod updater.")
