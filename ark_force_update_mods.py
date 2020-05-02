import time
from random import choice
from ark_manager import *
from paths import ARK_MODS_DIR
import os, shutil


from locks import Lock

from debug import get_logger
log = get_logger("arkbot")

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

lock = Lock()
if lock.locked:
    log.debug("Another script already running, exit...")
    sys.exit()

print ("Starting...")
log.info("Admin initialized force update mods.")

stop_server()
active_mods = get_active_mods()
log.info(f"Updating mods: {active_mods}")
update_mods(active_mods)
start_server()


print ("Remove lock...")
lock.unlock()
broadcast(f"Server was restarted to force update mods. Should be back up in a few minutes. {args.message}{choice(random_funny_bits)}", False)