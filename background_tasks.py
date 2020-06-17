'''
Log gamelog, online players, positions and chat
'''
from ark_manager import *
from gamechat_commands import parse_chat
from dbo import *
import functools

from datetime import datetime
import patreon




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
def log_chat_gamelog_ordered():
    log_chat()
    time.sleep(1)
    log_gamelog()

@catch_errors
def patreon_payout():
    # Only perform on day 1 of a month
    if not datetime.now().day == 1:
        log.debug("Not first day of the month, not paying out patrons.")
        return None


    first_run = False

    if not os.path.exists(PAYOUTS_FILE_PATH):
        write_config('payouts', {'last_payout_month': datetime.now().month})
        first_run = True

    payout_data = read_config("payouts")
    if datetime.now().month != payout_data['last_payout_month'] or first_run:
        log.info("Paying out patrons...")
        api_client = patreon.API(read_config("config")["patreon_token"])
        pledges = {}
        users = {}
        all_data = api_client.fetch_campaign_and_patrons()._all_resource_json_data()
        for data in all_data:
            if 'type' in data:
                if data['type'] == 'pledge':
                    pledges[data['relationships']['patron']['data']['id']] = data['attributes']
                elif data['type'] == 'user':
                    users[data['id']] = data['attributes']
        user_info = read_config("players")
        for user_id, pledge in pledges.items():
            active = pledge['declined_since'] == None
            log.info(f"{users[user_id]['email']} is paying {pledge['amount_cents'] / 100}$, active is {active}")
            if user_info[users[user_id]['email']] == None:
                log.warning(f"Tried to payout user with email {users[user_id]['email']} but it does not have SteamID set.")
                broadcast("There was a problem during payout to one of the patrons, SteamID not set, please contact administrator.", True)
                continue
            if not active:
                log.warning(f"User {users[user_id]['email']} canceled subscription. Not paying.")
                continue
            rcon_command(f"ScriptCommand TCsAR AddArcTotal {user_info[users[user_id]['email']]} {pledge['amount_cents'] / 100}")

    else:
        log.debug("Not paying out patrons because it's the same month as we payed already.")

if __name__ == "__main__":
    patreon_payout()