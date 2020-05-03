import os
import yaml
import requests
import sys
import subprocess
import re

from paths import *
from configuration import server

from linux_utils import run_shell_command_as_user

from locks import Lock

from discord_webhook import DiscordWebhook

from mcrcon import MCRcon


from moddodo import ModDodo

rp = realpath = os.path.dirname(os.path.realpath(__file__))

from debug import get_logger
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
    log.info("Checking for update...")
    ## workaround for conflicting file that can prevent getting the most recent version
    if os.path.isfile("/home/arkserver/Steam/appcache/appinfo.vdf"):
        os.remove("/home/arkserver/Steam/appcache/appinfo.vdf")

    pattern = re.compile(r"[0-9]{7,}")
    ## See if update is available
    ## should return a byte object as b'\t\t"branches"\n\t\t{\n\t\t\t"public"\n\t\t\t{\n\t\t\t\t"buildid"\t\t"3129691"\n'
    steamcmd = f"""{STEAMCMD} +login anonymous +app_info_update 1 +app_info_print 376030 +quit | sed -n '/"branches"/,/"buildid"/p' """
    steam_out = run_shell_command_as_user(steamcmd)
    new_vers = pattern.search(steam_out).group()

    with open("/home/arkserver/serverfiles/steamapps/appmanifest_376030.acf") as inFile:
        for line in inFile:
            if 'buildid' in line:
                curr_vers = pattern.search(line).group()
                break

    if int(new_vers) > int(curr_vers):
        return True
    elif int(new_vers) == int(curr_vers):
        log.info("Server reports up-to-date")
        return False

def get_active_mods():
    with open(GAMEUSERSETTINGS, "r", encoding="utf8") as f:
        user_settings = f.readlines()
    mods_list = None
    for line in user_settings:
        if line.startswith("ActiveMods"):
            mods_list = line.partition("=")[2].strip().split(",")
            break
    if not mods_list:
        return None
    else:
        return mods_list

def check_mod_versions():
    log.info ("Checking for mod updates...")


    return None # Return mod IDs that needs to be updated or None if none

import shutil

def update_mods(mod_ids):
    try:
        ModDodo(os.path.dirname(STEAMCMD),
                mod_ids,
                ARK_SERVER_DIR,
                False,
                False)
        return True
    except:
        log.error("Unable to update mods.", exc_info=True)
        return False

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

def fix_mods_permissions():
    fix_permissions(ARK_MODS_DIR)



def check_output(cmd):
    log.debug(f"Running shell command raw: {cmd}")
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    output = process.communicate()[0]
    if process.returncode != 0:
        log.warning(f"Command '{cmd}' exited with non standard exit code: {process.returncode}")
    log.debug(f"Command '{cmd}' output: {process.returncode}; {output}")
    return output




def update_server():
    log.info("Updating...")
    steamcmd = """/home/arkserver/arkserver update"""
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


def broadcast(message, discord=False):
    if discord:
        discord_message(f"[{server.name}] {message}")

    return rcon_command(f'broadcast {message}')

def serverchat(message, discord=False):
    if discord:
        discord_message(f"[{server.name}] {message}")
    return rcon_command(f'ServerChat {message}')

def discord_message(message):
    discord_webhook = DiscordWebhook(url=server.discord_webhook, content=message)
    response = discord_webhook.execute()

    return response


if __name__ == "__main__":
    print (listplayers())
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