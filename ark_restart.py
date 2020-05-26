import time
from random import choice
from ark_manager import *

from debug import get_logger
log = get_logger("ark_other_scripts")

from locks import Lock

import argparse
parser = argparse.ArgumentParser(description='Restart ark server.')
parser.add_argument("--message", dest='message', default=None, help="Message to add to broadcast, usually reason for restart.")
parser.add_argument("--nodelay", dest='nodelay', default=False,
                    help="Run without delay.")
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
log.info("Admin initialized restart.")
lock.lock("Locked for restart...")
if args.nodelay == False:
    broadcast(f"Server will restart in 60 minutes. {args.message}{choice(random_funny_bits)}", True)
    time.sleep(30 * 60)
    broadcast(f"Server will restart in 30 minutes. {args.message}{choice(random_funny_bits)}", True)
    time.sleep(15 * 60)
    broadcast(f"Server will restart in 15 minutes. {args.message}{choice(random_funny_bits)}", True)
    time.sleep(10 * 60)
    broadcast(f"Server will restart in 5 minutes. {args.message}{choice(random_funny_bits)}", True)
    time.sleep(5 * 60)
    broadcast(f"Server will restart in 10 seconds. {args.message}{choice(random_funny_bits)}", True)
    for i in range(1, 10):
        broadcast(f"Restart in {10 - i}...")
print ("Restarting...")
restart_server()
time.sleep(15 * 60)
print ("Remove lock...")
lock.unlock()
