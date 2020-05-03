import os

ARK_STEAMID = "346110"

APP_DIR = os.path.dirname(os.path.realpath(__file__))

HOME_DIR = r"/home/arkserver"

ARK_SERVER_DIR = os.path.join(HOME_DIR, "serverfiles")

ARK_MODS_DIR = os.path.join(ARK_SERVER_DIR, "ShooterGame", "Content", "Mods" )



STEAMCMD = r"/home/arkserver/steamcmd/steamcmd.sh"

STEAM_MODS_DIR = os.path.join("/home/arkserver/.local/share/Steam/steamapps/workshop/content", ARK_STEAMID)
CONFIGS_DIR = r"/home/arkserver/serverfiles/ShooterGame/Saved/Config/LinuxServer"
GAMEUSERSETTINGS = os.path.join(CONFIGS_DIR, "GameUserSettings.ini")

DOWNLOADS_DIR = os.path.join(APP_DIR, "downloads")


STANDARD_MODS = ["111111111", "Ragnarok", "TheCenter", "Valguero"]


