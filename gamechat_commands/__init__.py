import importlib
from ark_manager import *

class BaseSkill(object):
    def process(self, data):
        pass


skills = {}
for file in os.listdir(os.path.join(rp, "gamechat_commands")):
    if not file.startswith("_") and not file.endswith("_"):
        name, ext = os.path.splitext(file)
        if ext.lower() == ".py":
            try:
                skills[name] = importlib.import_module(f'gamechat_commands.{name}').Skill()
            except Exception as e:
                log.warning (f"Could not load module {name}, {str(e)}")

def parse_chat(chat, raw=False):
    if raw:
        messages = raw_chat_to_messages(chat)
    else:
        messages = chat

    for message in messages:
        text = message.message.strip()
        if text.startswith("/"):
            text = text.replace("/", "")
            command, sep, data = text.partition(" ")
            if command in skills:
                skills[command].process(data)