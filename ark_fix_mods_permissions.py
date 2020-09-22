import time
from random import choice
from ark_manager import *

from debug import get_logger

log = get_logger("ark_other_scripts")


log.info("Admin initialized fix mods permissions.")
try:
    fix_mods_permissions()
    log.info(f"Permissions fix ran without errors.")
except Exception as e:
    log.error("Permission fix ran with errors.", exc_info=True)
