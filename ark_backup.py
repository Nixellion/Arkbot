import os
import shutil
from ark_manager import *

from paths import *

from debug import get_logger
log = get_logger("arkbot")


def back_up(folder=None):
    if folder:
        backup_dir = os.path.join(BACKUPS_DIR, folder)
    else:
        backup_dir = BACKUPS_DIR

    log.info(f"Backing up server data into {backup_dir}")

    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir, exist_ok=True)

    for filepath in BACKUP_FILES:
        filename = os.path.basename(filepath)
        dest = os.path.join(backup_dir, filename)
        log.debug(f"Copying {filepath} to {dest}")
        shutil.copy(filepath, dest)

    log.info("Backup complete.")


if __name__ == "__main__":

    from locks import Lock
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

    lock = Lock()

    if lock.locked:
        log.debug("Another script already running, exit...")
        sys.exit()

    lock.lock()
    back_up()
    lock.unlock()
else:
    print ("Name not main just import")