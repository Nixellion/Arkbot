import time
from random import choice
from ark_manager import *

from debug import get_logger
log = get_logger("ark_updater")

from locks import Lock

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

def update():
    lock = Lock()

    if lock.locked:
        log.debug("Another script already running, exit...")
        sys.exit()

    if check_version():
        print ("Update found!")
        log.info("New version found, performing update.")
        lock.lock("Game updater.")
        run_with_delay(update_server, message="Update detected. ")
        update_server()
        time.sleep(10 * 60)
        broadcast("Update finished. Server should be up and running by now.", True)
        time.sleep(20 * 60)
        lock.unlock()
    else:
        log.debug("No new versions found.")
        print ("No new versions.")

if __name__ == "__main__":
    update()