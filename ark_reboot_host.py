from ark_manager import *
import time
from random import choice



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

def prompt_sudo():
    ret = 0
    if os.geteuid() != 0:
        msg = "[sudo] password for %u:"
        ret = subprocess.check_call("sudo -v -p '%s'" % msg, shell=True)
    return ret



if prompt_sudo() != 0:
    log.warning("Can't run reboot script, need root\sudo access.")
    sys.exit()



lock = Lock()
if lock.is_locked:
    log.debug("Another script already running, exit...")
    sys.exit()



print("Starting...")
log.info("Admin initialized restart.")
lock.lock()
broadcast(f"Cluster will reboot in 60 minutes. {args.message}{choice(random_funny_bits)}", True, True)
time.sleep(30 * 60)
broadcast(f"Cluster will reboot in 30 minutes. {args.message}{choice(random_funny_bits)}", True, True)
time.sleep(15 * 60)
broadcast(f"Cluster will reboot in 15 minutes. {args.message}{choice(random_funny_bits)}", True, True)
time.sleep(10 * 60)
broadcast(f"Cluster will reboot in 5 minutes. {args.message}{choice(random_funny_bits)}", True, True)
time.sleep(5 * 60)
broadcast(f"Cluster will reboot in 10 seconds. {choice(random_funny_bits)}", True, True)
for i in range(1, 10):
    broadcast(f"Restart in {10 - i}...")
print("Remove lock...")
lock.unlock()
print("Restarting...")
reboot_server()

