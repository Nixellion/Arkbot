# from configuration import read_config
#
# players = read_config("players")
#
# for email, player in players.items():
#     steamid = player['steamid']
#     patron = player.get("patron", None)
#     if patron:
#         print (steamid, patron)

from ark_manager import *
from gamechat_commands import parse_chat
from dbo import *
import functools

from datetime import datetime
import patreon

from debug import get_logger
log = get_logger("patreon")

def patreon_payout():
    # Only perform on day 1 of a month
    first_run = False
    now = datetime.now()

    if not os.path.exists(PAYOUTS_FILE_PATH):
        write_config('payouts', {})
        first_run = True

    payout_data = read_config("payouts")

    log.info("Checking payout information...")
    payout_emails = []
    for email, info in payout_data.items():
        if now.month > info['last_payout_month'].month and now > info['last_payout_month']:
            log.info(f"User {email} added for payout check.")
            payout_emails.append(email)

    log.info(f"Payout emails {payout_emails}")

    if len(payout_emails) > 0:
        log.info(f"Gathering patreon api info...")
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
            if user_info[users[user_id]['email']] == None:
                log.warning(f"Tried to payout user with email {users[user_id]['email']} but it does not have SteamID set.")
                broadcast("There was a problem during payout to one of the patrons, SteamID not set, please contact administrator.", True)
                continue
            if not active:
                log.warning(f"User {users[user_id]['email']} canceled subscription. Not paying.")
                continue
            log.info(f"{users[user_id]['email']} is paying {pledge['amount_cents'] / 100}$, active is {active}")
            if users[user_id]['email'].strip() in payout_emails:
                log.info(f"Paying out user {users[user_id]['email'].strip()}")
                rcon_command(f"ScriptCommand TCsAR AddArcTotal {user_info[users[user_id]['email']]} {pledge['amount_cents'] / 100}")
            else:
                log.inro (f"NOT paying out user {users[user_id]['email'].strip()} because it was not found in payout_emails - probably already payed.")

        else:
            log.debug("Not paying out patrons because it's the same month as we payed already.")
    else:
        log.info("Looks like everyone received their payment, exit.")

if __name__ == "__main__":
    patreon_payout()