# Arkbot
Ark server manager working with LinuxGSM and RCON

## Status

Active development, it works but I would not recommmend it for production use yet. Did not go through any long period of testing yet, still a lot of things are subject to change.

## Overview

When I started by own Ark server cluster I had some pretty limited resources, an low spec (ish) LenovoThink Center, with just 10 Gigs of RAM. This, my previous experience with Proxmox and Linux servers and just the idea that they are more stable were the reasons why I went with Linux.

I looked around and tried different existing control panels for Ark or general servers, and most of them were either too bloated, not free or lacking features I needed. So I decided to go with LinuxGSM as the core of game manager and write my own server manager on  top of this.

This is how this Arkbot was born. I will probably rename it at some point, as I found out there's another project with the same name.

Shoutout to projects like Moddodo and (Linux Ark Dedicated Server)[https://github.com/Ekagrah/Linux-Ark-Dedicated-Server] where I did look up some code and logic from, namely checking for game updates and updating mods. Moddodo's code base was taken, updated and integrated into Arkbot.

## Features

- Discord alerts using a webhook
- Update checker script that you can run manually or with a cronjob. Checks for update, and if updates is available sends notifications into Discord and over RCON into the game, warning players about a restart 60, 30, 15, 10, 5 minutes before it happens, with a 10 second countdown at the end (only in the game).
- Mod updater which works much the same way, but at a shorter delay because if mods are out of date chance's are people can't even join the server. You don't need to use Automanagemods as this mod updater will check, download, unpack and move mods manually. I personally found Automanagemods to be extremely buggy and unreliable. This script, on the other hand, so far works wonders. Thanks to Moddodo developers for providing the core of this fucntionality.
- Gamelog parser that checks game logs every few seconds and parses them into an SQLite databse which can be easily queried. Stores all events that happen in game and tribe logs, kills, tames, destructions, chat messages and more.
- Chat recorder. It's rudimentary to gamelog parser as it already records chat messages as well, but just in case chat parses simply writes all messages into a simple txt file.
- Web panel where you can see players online, chat messages, send admin messages into game chat, view game log, dashboard log and perform actions like force update, force mod updates, server restart, host system reboot and the like. Some of these actions can take a custom "Message" which will be displayed in Discord and server alerts.
- Backup and restore of server's configuration and save files (works but WIP, to be improved)
- Ingame chat commands. Currently only has /playercount which sends a message saying how many players are currently on the server. Can be expanded easily.

## Planned features

- Bounty hunter's event. Randomly pick one of the online players and place a bounty on his head. Give money to whoever kills him. Based on gamelog and TCsAutoRewards mod.
- Patreon supporters automatic monthly rewards. Based on patreon API and TCsAutoRewards
- Sending custom RCON commands to the server through the Web panel
- Config files editor

## Installation
This guide is for Debian based OSes (Debian, Ubuntu, etc). Should work with other systemd based OSes as well.

First install LinuxGSM and arkserver: https://linuxgsm.com/lgsm/arkserver/

Now this should be done as root user. Or use sudo if you wish, but as of right now bot is designed to work from root user.

```
cd /home/arkserver
git clone https://github.com/Nixellion/Arkbot.git
cd Arkbot/config
cp config-example.yaml config.yaml
nano config.yaml
```

Edit config and save.
Now let's install dependencies.

```
cd /home/arkserver/Arkbot
apt install python3-pip
pip3 install -r requirements.txt
```

Now let's make it a service that runs on startup and can be controlled with sytemd.

```
cd .. 
cp arkdashboard.service /etc/systemd/system
systemctl daemon-reload
systemctl enable arkdashboard.service
service arkdashboard start
systemctl status arkdashboard.service
```

That's it, it should be up and running. Check your server's LAN IP and port 1117 or localhost:1117 if it's the same machine you're on.

Next up is to set up a conjob to run ark_updater.py and ark_mod_updater.py every few minutes. I have it set to run every 5. If it detects and update it will create a .lock file so other runs of this script will just exit if they see the lock file.

I usually set cronjobs up with Webmin, if requested will look up and add commands to set those crons up with CLI here.

## Technologies used

- Python
- Flask
- Peewee
- MCRcon
- Bootstrap 4
- JS
