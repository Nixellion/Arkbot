'''
Log gamelog, online players, positions and chat
'''
from ark_manager import *
from gamechat_commands import parse_chat
from dbo import *
import functools

# region Logger
import logging
from debug import setup_logging

log = logger = logging.getLogger("ark_dashboard")
setup_logging()
# endregion

def catch_errors(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            log.warning(traceback.format_exc())

    return wrapped

@catch_errors
def log_gamelog():
    gamelog = getgamelog()
    if gamelog != None:
        if gamelog.strip():
            log.debug(f"Save gamelog to file: {gamelog}")
            with open(os.path.join(APP_DIR, "gamelog.txt"), "a+", encoding="utf-8") as f:
                f.write(gamelog)

            for line in gamelog.split("\n"):
                if line.strip():
                    log.debug(f"Parsing line: {line}")
                    store_log_data(line)
        log.debug("Gamelog is empty.")
    else:
        #log.debug("No gamelog updates received from server.")
        pass

@catch_errors
def log_chat():
    chat = get_chat_messages()

    if chat != None:
        chat_text = ""
        for message in chat:
            chat_text += f"{message.player}: {message.message}\n"

        with open(os.path.join(APP_DIR, "chatlog.txt"), "a+", encoding="utf-8") as f:
            f.write(chat_text)

        parse_chat(chat)