import os

from debug import get_logger
log = get_logger("default")

ARK_STEAMID = "346110"

APP_DIR = os.path.dirname(os.path.realpath(__file__))

DATABASE_PATH = os.path.join(APP_DIR, "database.db")

CONFIG_FILE_PATH = os.path.join(APP_DIR, "config", "config.yaml")

HOME_DIR = r"/home/arkserver"

ARK_SERVER_DIR = os.path.join(HOME_DIR, "serverfiles")

ARK_MODS_DIR = os.path.join(ARK_SERVER_DIR, "ShooterGame", "Content", "Mods" )

ARK_SAVED_DIR = os.path.join(HOME_DIR, "serverfiles", "ShooterGame", "Saved")

STEAMCMD = os.path.join(HOME_DIR, ".steam", "steamcmd", "steamcmd.sh")
STEAMCMD_STEAMAPPS_DIR = os.path.join(HOME_DIR, ".local", "share", "Steam", "steamapps")
STEAMCMD_MODS_DIR = os.path.join(STEAMCMD_STEAMAPPS_DIR, "workshop", "content", ARK_STEAMID)


log.debug(f"STEAMCMD: {STEAMCMD}")



ARK_CONFIGS_DIR = os.path.join(ARK_SAVED_DIR, "Config", "LinuxServer")

GAMEUSERSETTINGS = os.path.join(ARK_CONFIGS_DIR, "GameUserSettings.ini")

DOWNLOADS_DIR = os.path.join(APP_DIR, "downloads")

LGSM_CONFIG_DIR = os.path.join(HOME_DIR, "lgsm", "config-lgsm", "arkserver")

STANDARD_MODS = ["111111111", "Ragnarok", "TheCenter", "Valguero"]

BACKUPS_DIR = os.path.join(APP_DIR, "backups")

KNOWN_MAPS = ["TheIsland", "Genesis", "Aberration_P", "Extinction", "ScorchedEarth_P"]

BACKUP_FILES = [
    CONFIG_FILE_PATH,
    DATABASE_PATH,
    os.path.join(ARK_CONFIGS_DIR, "Game.ini"),
    os.path.join(ARK_CONFIGS_DIR, "GameUserSettings.ini"),
]

BACKUP_DIRS = []

for filename in ["_default.cfg", "arkserver.cfg",  "common.cfg"]:
    BACKUP_FILES.append(os.path.join(LGSM_CONFIG_DIR, filename))

map_save_found = False
for MAP in KNOWN_MAPS:
    MAP_DIR_PATH = os.path.join(ARK_SAVED_DIR, MAP)
    if os.path.exists(MAP_DIR_PATH):
        map_save_found = True
        BACKUP_DIRS.append(MAP_DIR_PATH)


if not map_save_found:
    for i in range(0, 10):
        log.error("DANGER! NO MAP SAVE FOLDER FOUND! IF ITS A NEW MAP PLEASE EDIT paths.py TO ADD IT TO KNOWN_MAPS VARIABLE!!!")



