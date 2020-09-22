import time
from random import choice
from ark_manager import *

from debug import get_logger

log = get_logger("ark_other_scripts")


print("Starting...")
log.info("Admin initialized dino wipe.")
print("Wiping dinos...")
log.info(f"Dino wipe result: {destroy_wild_dinos()}")
print("Remove lock...")
