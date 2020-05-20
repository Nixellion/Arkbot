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
parser.add_argument("--nodelay", dest='nodelay', default=False,
                    help="Run without delay.")
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
    modids, mod_names, memory = check_mod_versions()
    if modids != None:
        log.info("New mod version found, performing update.")
        lock.lock("Locked for update...")
        if args.nodelay == False:
            if len(modids) > 1:
                delay_with_notifications(message=f"Updating mods: {mod_names}. ")
            else:
                delay_with_notifications(message=f"Updating mod: {mod_names}. ")
        stop_server()
        log.info(f"Updating mods: {modids}")
        try_counter = 0
        success = False
        while not success or try_counter >= 10:
            success = update_mods(modids)
            if not success:
                log.warning("Mod updates failed. Retrying in a minute.")
                try_counter += 1
                time.sleep(60)
        if success:
            fix_mods_permissions()
            start_server()
            time.sleep(10 * 60)
            lock.unlock()
        else:
            broadcast("Mod update failed after 10 retries. Manual intervention is required. @Nix#8175 notified.", True)
    else:
        log.debug("No new mod version found.")



if __name__ == "__main__":
    mod_updater()

