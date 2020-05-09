'''
Log gamelog, online players, positions and chat
'''
from ark_manager import *
from gamechat_commands import parse_chat
from dbo import *
import functools

from datetime import datetime


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


@catch_errors
def patreon_payout():
    # Only perform on day 1 of a month
    if not datetime.now().day == 1:
        return None

    first_run = False

    if not os.path.exists(PAYOUTS_FILE_PATH):
        write_config('payouts', {'last_payout_month': datetime.now().month})
        first_run = True

    payout_data = read_config("payouts")
    if datetime.now().month != payout_data['last_payout_month'] or first_run:
        pass