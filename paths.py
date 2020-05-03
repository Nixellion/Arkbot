import os


ARK_STEAMID = "346110"

APP_DIR = os.path.dirname(os.path.realpath(__file__))

DATABASE_PATH = os.path.join(APP_DIR, "database.db")

CONFIG_FILE_PATH = os.path.join(APP_DIR, "config", "config.yaml")

HOME_DIR = r"/home/arkserver"

ARK_SERVER_DIR = os.path.join(HOME_DIR, "serverfiles")

ARK_MODS_DIR = os.path.join(ARK_SERVER_DIR, "ShooterGame", "Content", "Mods" )



STEAMCMD = r"/home/arkserver/steamcmd/steamcmd.sh"

STEAM_MODS_DIR = os.path.join("/home/arkserver/.local/share/Steam/steamapps/workshop/content", ARK_STEAMID)

CONFIGS_DIR = r"/home/arkserver/serverfiles/ShooterGame/Saved/Config/LinuxServer"

GAMEUSERSETTINGS = os.path.join(CONFIGS_DIR, "GameUserSettings.ini")

DOWNLOADS_DIR = os.path.join(APP_DIR, "downloads")

LGSM_CONFIG_DIR = os.path.join(HOME_DIR, "lgsm", "config-lgsm", "arkserver")

STANDARD_MODS = ["111111111", "Ragnarok", "TheCenter", "Valguero"]

BACKUPS_DIR = os.path.join(APP_DIR, "backups")

BACKUP_FILES = [
    CONFIG_FILE_PATH,
    DATABASE_PATH,
    os.path.join(CONFIGS_DIR, "Game.ini"),
    os.path.join(CONFIGS_DIR, "GameUserSettings.ini"),
]


for filename in ["_default.cfg", "arkserver.cfg",  "common.cfg"]:
    BACKUP_FILES.append(os.path.join(LGSM_CONFIG_DIR, filename))