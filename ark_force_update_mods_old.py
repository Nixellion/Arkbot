import time
from random import choice
from ark_manager import *
from paths import ARK_MODS_DIR
import os, shutil


from locks import Lock

import logging
from debug import setup_logging

log = logging.getLogger("ark_manager")
setup_logging()

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

# rm -rf /home/arkserver/serverfiles/ShooterGame/Content/Mods && mkdir /home/arkserver/serverfiles/ShooterGame/Content/Mods
# \\192.168.1.185\root\home\arkserver\.local\share\Steam\steamapps\workshop\content\346110

stop_server()
for file in os.listdir(ARK_MODS_DIR):
    filepath = os.path.join(ARK_MODS_DIR, file)
    try:
        if os.path.isfile(filepath):
            os.remove(filepath)
        elif os.path.isdir(filepath):
            shutil.rmtree(filepath)
    except Exception as e:
        log.error(f"Could not remove {filepath}", exc_info=True)


print ("Remove lock...")
lock.unlock()
broadcast(f"Server was restarted to force update mods. Should be back up in a few minutes as it redownloads mods and starts up. {args.message}{choice(random_funny_bits)}", False)