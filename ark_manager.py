import os
import yaml
import requests
import sys
import subprocess
import re
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

from paths import *
from configuration import server, read_config, write_config

from linux_utils import run_shell_command_as_user, run_shell_command_as_user_check_output

from locks import Lock

from discord_webhook import DiscordWebhook

from mcrcon import MCRcon

from moddodo import ModDodo

rp = realpath = os.path.dirname(os.path.realpath(__file__))

from debug import get_logger, catch_errors

log = get_logger("ark_manager")

random_funny_bits = [
    "Time to find shelter!",
    "Don't forget to hide your Dodos!",
    "Run, forrest, run!",
    "Time to hide!",
    "Find a good place to fall unconscious!",
    "Sorry if you're taming something, will have to try again...",
    "Why did the survivor not care? He wasn't ready to give a poop.",
    "In Soviet ARK, dinos tame you!",
    "What's the worst thing about bugs in ark? They can kill you literally and figuratively.",
    "The wolves are everywhere. Things are truly looking dire.",
    "Lemme just mosa on ovi here and pachy a few things. I need to be leaving bronto.",
    "Not to introodon on your conversation, but I gotta ask: what's your angler on all this?",
    "Taking your bird on a spy mission? Secret Argent Man.",
    "The oviraptor is eggcellent.",
    "ARK is a very resource heavy game. It takes many trilobytes of memory to run.",
    "I went to tame a giga but I got alpha rex'd",
    "I wanna tame an Iguanadon. Tribe leader says Iguanadon-t...",
    "Mess with the dodo and you'll get the choko"
]


class Player(object):
    def __init__(self, id, name, steam_id):
        self.id = id
        self.name = name
        self.steam_id = steam_id

    def __repr__(self):
        return f"Player: {self.id} - {self.name} - {self.steam_id}"


class ChatMessage(object):
    def __init__(self, player, message):
        self.player = player
        self.message = message

    def __repr__(self):
        return f"{self.player} - {self.message}"


def rcon_command(command):
    lock = Lock("warning")
    try:
        log.debug(f"Running RCON command: {command}")
        with MCRcon(server.ip, server.password, port=server.rcon_port) as mcr:
            resp = mcr.command(command)

        if lock.is_locked:
            lock.unlock()

        if "Server received, But no response!!" in resp or "No Players Connected" in resp:
            return None

        return resp
    except ConnectionRefusedError:
        log.warning("Unable to connect to RCON, is server down?")

    except Exception as e:
        lock.lock(str(e))
        log.error(str(e), exc_info=True)

        return None


def getchat():
    return rcon_command('getchat')


def getgamelog():
    return rcon_command('getgamelog')


def destroy_wild_dinos():
    return rcon_command('destroywilddinos')


def raw_chat_to_messages(chat):
    messages = []
    for line in chat.split("\n"):
        # log.debug(f"raw_chat_to_messages, line: {line}")
        player, sep, message = line.partition(": ")
        # log.debug(f"raw_chat_to_messages, parsed: {player}-{sep}-{message}")
        if player.strip() != "" and message.strip() != "":
            messages.append(ChatMessage(player, message))
    return messages


def get_chat_messages(raw=False):
    chat = getchat()
    if raw:
        return chat
    if chat:
        return raw_chat_to_messages(chat)
    else:
        return None


def listplayers():
    players_data = rcon_command('listplayers')
    log.debug(f"listplayers {players_data}")
    players = []
    if players_data:
        for line in players_data.split("\n"):
            if line.strip() != "":
                id, line = line.split(".")
                name, steam_id = line.split(",")
                id = int(id.strip())
                name = name.strip()
                steam_id = int(steam_id.strip())
                players.append(Player(id, name, steam_id))
    return players


def check_version():
    """Check if update to server has been posted"""
    log.debug("Checking for update...")
    ## workaround for conflicting file that can prevent getting the most recent version
    if os.path.isfile(STEAM_APPCACHE_FILEPATH):
        log.debug(f"Remove {STEAM_APPCACHE_FILEPATH}.")
        os.remove(STEAM_APPCACHE_FILEPATH)
    else:
        log.debug(f"{STEAM_APPCACHE_FILEPATH} does not exist.")

    pattern = re.compile(r"[0-9]{7,}")
    ## See if update is available
    ## should return a byte object as b'\t\t"branches"\n\t\t{\n\t\t\t"public"\n\t\t\t{\n\t\t\t\t"buildid"\t\t"3129691"\n'
    steamcmd = f"""{STEAMCMD} +login anonymous +app_info_update 1 +app_info_print 376030 +quit | sed -n '/"branches"/,/"buildid"/p' """
    steam_out = run_shell_command_as_user_check_output(steamcmd).decode()
    log.debug(f"Steam out: {steam_out}")
    new_vers = pattern.search(steam_out).group()

    with open("/home/arkserver/serverfiles/steamapps/appmanifest_376030.acf") as inFile:
        for line in inFile:
            if 'buildid' in line:
                curr_vers = pattern.search(line).group()
                break
    log.info(f"Steam game versions - new: {new_vers}; current: {curr_vers}")
    if int(new_vers) > int(curr_vers):
        return {"new_vers": new_vers}
    elif int(new_vers) == int(curr_vers):
        log.debug("Server reports up-to-date")
        return None


check_update = check_version


def get_active_mods():
    with open(GAMEUSERSETTINGS, "r", encoding="utf8") as f:
        user_settings = f.readlines()
    mods_list = None
    for line in user_settings:
        if line.startswith("ActiveMods"):
            mods_list = line.partition("=")[2].strip().split(",")
            break
    log.debug(f"Found active mods: {mods_list}")
    if not mods_list:
        return None
    else:
        return mods_list


@catch_errors
def check_mod_versions(verbose=True):
    '''
    Check for mod updates

    :param verbose: In non verbose mode will simply return True or False when it finds first mod to be updated.
    In verbose mode will output modids_to_update, mod_names, memory, data required for updater function to work.
    :return:  See above
    '''
    log.info("Checking for mod updates...")

    modids = get_active_mods()

    memory = read_config("mod_updater_data")
    if not memory:
        memory = {}
        for modid in modids:
            memory[modid] = {'last_update': datetime(year=1991, month=1, day=1)}
        # write_config("mod_updater_data", memory)

    for modid in modids:
        if modid not in memory:
            memory[modid] = {'last_update': datetime(year=1991, month=1, day=1)}
    write_config("mod_updater_data", memory)

    modids_to_update = []
    mod_names = []

    for modid in modids:
        log.debug(f"Querying info on mod {modid}")
        mod_info_html = requests.get(f"https://steamcommunity.com/sharedfiles/filedetails/?id={modid}").text
        soup = BeautifulSoup(mod_info_html, features="html.parser")
        date_string = \
            soup.find("div", {"id": "mainContents"}).find("div", {"class": "workshopItemPreviewArea"}).find_all(
                "div", {"class": "detailsStatRight"})[2].text

        try:
            workshop_updated_date = datetime.strptime(date_string, "%d %b, %Y @ %H:%M%p")
        except ValueError:
            workshop_updated_date = datetime.strptime(date_string, "%d %b @ %H:%M%p")
            workshop_updated_date = workshop_updated_date.replace(year=datetime.now().year)

        if workshop_updated_date > memory[modid]['last_update']:
            log.debug(
                f"Update required for mod: {modid}; Last updated date: {memory[modid]['last_update']}; Workshop date: {workshop_updated_date}")
            modids_to_update.append(modid)
            mod_name = soup.find("div", {"class": "workshopItemTitle"}).text
            mod_names.append(mod_name)
            # memory[modid]['last_update'] = datetime.now()
        # write_config("mod_updater_data", memory)

    if len(modids_to_update) > 0:
        log.info(f"Update required for mods: {modids_to_update}")
        data = {
            'mod_ids': modids_to_update,
            'mod_names': mod_names,
        }
        return data
    else:
        log.info("All mods are up to date.")
        return None


import shutil


@catch_errors
def update_mods(mod_ids, **kwargs):
    success = True
    try:
        ModDodo(os.path.dirname(STEAMCMD),
                mod_ids,
                ARK_SERVER_DIR,
                False,
                False)
    except:
        log.error("Unable to update mods.", exc_info=True)
        success = False

    if success:
        memory = read_config("mod_updater_data")
        for modid in mod_ids:
            memory[modid]['last_update'] = datetime.now()
        write_config("mod_updater_data", memory)

    return success


def fix_permissions(path):
    try:
        if os.path.isdir(path):
            log.debug(f"Fix permissions recursively for directory {path}")
            run_shell_command_as_user(f"chown -R arkserver:arkserver {path}", user='root')
        else:
            log.debug(f"Fix permissions for file {path}")
            run_shell_command_as_user(f"chown arkserver:arkserver {path}", user='root')
        return True
    except:
        log.error("Unable to fix mod permissions.", exc_info=True)
        return False


def fix_mods_permissions(*args, **kwargs):
    fix_permissions(ARK_MODS_DIR)
    fix_permissions(ARK_CONFIGS_DIR)
    fix_permissions(ARK_SAVED_DIR)


import zipfile


def backup_savegames():
    log.debug(f"Backing up savegames: {ARK_SAVED_DIR} to {BACKUPS_DAILY_ZIP}")
    save_exts = ['.ark', '.arktribe', '.tribebak', '.arkprofile', '.profilebak', '.arktributetribe']
    existing_files = []
    if os.path.exists(BACKUPS_DAILY_ZIP):
        with zipfile.ZipFile(BACKUPS_DAILY_ZIP, 'r') as f:
            for fn in f.namelist():
                existing_files.append(os.path.normpath(fn))
            # log.debug(existing_files)
    zipf = zipfile.ZipFile(BACKUPS_DAILY_ZIP, 'a', zipfile.ZIP_LZMA)
    log.debug(f"ZIPFILE: {BACKUPS_DAILY_ZIP}")
    # sys.exit()
    for root, dirs, files in os.walk(ARK_SAVED_DIR, topdown=False):
        for filename in files:
            name, ext = os.path.splitext(filename)
            if ext.lower() in save_exts:
                filepath = os.path.join(root, filename)
                relative_path = os.path.normpath(os.path.relpath(filepath, os.path.join(ARK_SAVED_DIR, '..')))
                # print(f"{relative_path}; {relative_path not in existing_files}")
                if relative_path not in existing_files:
                    log.debug(f"Zipping {filepath} as {relative_path}...")
                    zipf.write(filepath, relative_path)
    zipf.close()


def health_check_diskspace():
    lock = Lock("DiskSpace")
    total, used, free = shutil.disk_usage("/")
    free_mb = free / 1024 / 1024
    log.debug(f"[Healthcheck] Free disk space: {str(free_mb).zfill(2)}MB")

    if free_mb < 500:
        if not lock.locked:
            discord_message(f"[{server.name}] Free disk space is running low. {str(free_mb).zfill(2)}MB is available.")
            lock.lock()
            try:
                os.system('logrotate /etc/logrotate.d/rsyslog')
                os.system('rm /var/log/*.1')
            except Exception as e:
                log.error("Attempted rotating logs: {}".format(e))
    else:
        if lock.locked:
            discord_message(f"[{server.name}] Disk space issue was fixed. {str(free_mb).zfill(2)}MB is now available.")
            lock.unlock()


def check_output(cmd):
    log.debug(f"Running shell command raw: {cmd}")
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    output = process.communicate()[0]
    if process.returncode != 0:
        log.warning(f"Command '{cmd}' exited with non standard exit code: {process.returncode}")
    log.debug(f"Command '{cmd}' output: {process.returncode}; {output}")
    return output


def update_server(*args, **kwargs):
    log.info("Updating...")
    # steamcmd = """/home/arkserver/arkserver update""" # Had an issue with SteamCMD failing to check new version
    # while Arkbot was able to detect new version. Force update makes more sense this way.
    steamcmd = """/home/arkserver/arkserver force-update"""
    cmd_out = run_shell_command_as_user(steamcmd)
    log.info(str(cmd_out))


def restart_server():
    log.info("Restarting...")
    steamcmd = """/home/arkserver/arkserver restart"""
    cmd_out = run_shell_command_as_user(steamcmd)
    log.info(str(cmd_out))


def stop_server():
    log.info("Stopping...")
    steamcmd = """/home/arkserver/arkserver stop"""
    cmd_out = run_shell_command_as_user(steamcmd)
    log.info(str(cmd_out))


def start_server():
    log.info("Starting...")
    steamcmd = """/home/arkserver/arkserver start"""
    cmd_out = run_shell_command_as_user(steamcmd)
    log.info(str(cmd_out))


def reboot_server():
    log.info("Rebooting...")
    steamcmd = """reboot now"""
    cmd_out = run_shell_command_as_user(steamcmd, user='root')
    log.info(str(cmd_out))


def broadcast(message, discord=False, cluster=False):
    if discord:
        if cluster:
            server_name = "All"
        else:
            server_name = server.name
        discord_message(f"[{server_name}] {message}")

    return rcon_command(f'broadcast {message}')


def serverchat(message, discord=False):
    if discord:
        discord_message(f"[{server.name}] {message}")
    return rcon_command(f'ServerChat {message}')


def discord_message(message):
    discord_webhook = DiscordWebhook(url=server.discord_webhook, content=message)
    response = discord_webhook.execute()

    return response


def run_with_lock(func, lock_name="general", message=""):
    log.debug(f"Running {func.__name__} with lock...")

    lock = Lock(lock_name)
    if lock.locked:
        log.debug(f"Another script already running, abort running {func.__name__}...")
        sys.exit()

    lock.lock(message)

    func()

    log.debug(f"{func.__name__} finished. Removing lock.")
    lock.unlock()


from random import choice
import time


def delay_with_notifications(delay_minutes=(30, 15, 10, 5), message=""):
    log.debug(f"delay_with_notifications: {delay_minutes}; {message}")

    total = sum(delay_minutes)

    for dm in delay_minutes:
        broadcast(f"Server will restart in {total} minutes. {message}{choice(random_funny_bits)}", True)
        total -= dm
        time.sleep(dm * 60)

    for i in range(1, 10):
        broadcast(f"Restart in {10 - i}...")


def run_with_delay(func, delay_minutes=(30, 15, 10, 5), message=""):
    log.info(f"Running {func.__name__} with delay: {delay_minutes}")

    delay_with_notifications(delay_minutes, message)

    log.info(f"Running {func.__name__}...")
    func()


if __name__ == "__main__":
    print(listplayers())
    '''
    import paramiko


    def ssh_command(server, commands):
        if not isinstance(commands, list):
            commands = [commands]

        ip = server.ip
        username = 'root'
        password = '4maSrhenjq'
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=username, password=password)
        output = ""

        for command in commands:
            print ("ssh:", command)
            ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command, get_pty=True)

            for line in iter(ssh_stdout.readline, ""):
                print (">", line)
                output += line

        return output


    print(ssh_command(server, [
        "su arkserver",
        "cd ~",
        "./arkserver details"
    ]))
    '''
