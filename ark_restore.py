import os
import shutil
from ark_manager import *

from paths import *

from debug import get_logger
log = get_logger("ark_other_scripts")

from bro_utils import copytree

def restore(folder=None):
    if folder:
        backup_dir = os.path.join(BACKUPS_DIR, folder)
    else:
        backup_dir = BACKUPS_DIR

    log.info(f"Restoring server data from {backup_dir}")

    backup_dir_files = os.listdir(backup_dir)

    for restore_filepath in BACKUP_FILES:
        filename = os.path.basename(restore_filepath)
        if filename in backup_dir_files:
            backup_filepath = os.path.join(backup_dir, filename)
            log.debug(f"Copying {backup_filepath} to {restore_filepath}")
            try:
                shutil.copy(backup_filepath, restore_filepath)
                fix_permissions(restore_filepath)
            except shutil.SameFileError:
                log.debug(f"Same file, not copying {backup_filepath} - {restore_filepath}")
            except:
                log.error(f"Error copying file {backup_filepath}!", exc_info=True)
        else:
            log.warning(f"Could not find {restore_filepath} in backup directory!")

    for restore_dirpath in BACKUP_DIRS:
        dirname = os.path.basename(os.path.normpath(restore_dirpath))
        if dirname in backup_dir_files:
            backup_dirpath = os.path.join(backup_dir, dirname)
            if not os.path.exists(restore_dirpath):
                os.makedirs(restore_dirpath, exist_ok=True)
            run_shell_command_as_user(f"rm -rf {restore_dirpath}/*", user="root")
            log.debug(f"Copying {backup_dirpath} to {restore_dirpath}")
            try:
                copytree(backup_dirpath, restore_dirpath)
                fix_permissions(restore_dirpath)
            except:
                log.error(f"Error copying directory {backup_dirpath}!", exc_info=True)
        else:
            log.warning(f"Could not find {restore_dirpath} in backup directory!")

    log.info("Restore complete.")


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
    restore()
    lock.unlock()
else:
    print ("Name not main just import")