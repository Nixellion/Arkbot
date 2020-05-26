import time
from random import choice
from ark_manager import *
from paths import ARK_MODS_DIR
import os, shutil


from locks import Lock

from debug import get_logger
log = get_logger("ark_mods_updater")

import argparse
parser = argparse.ArgumentParser(description='Restart ark server.')
parser.add_argument("--message", dest='message', default=None, help="Message to add to broadcast, usually reason for restart.")
args = parser.parse_args()

if args.message:
    args.message = args.message.strip()
    if not args.message.endswith("."):
        args.message = args.message + ". "
    else:
        args.message = args.message + " "

def force_update_mods():
    log.info("Admin initialized force update mods.")
    stop_server()
    active_mods = get_active_mods()
    log.info(f"Updating mods: {active_mods}")
    update_mods(active_mods)
    fix_mods_permissions()
    start_server()

if __name__ == "__main__":

    run_with_lock(force_update_mods, message="Force update mods.")