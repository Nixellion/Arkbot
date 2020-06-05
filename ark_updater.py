RESTART_DELAY = 60
CRON_INTERVAL = 10

import time
from random import choice
import ark_manager as am
from configuration import read_config, write_config
import yaml

from datetime import datetime, timedelta

import os

from debug import get_logger
log = get_logger("ark_updater")

from locks import Lock

def perform_checks(checks=None, auto_update=True):
    if not checks:
        checks = read_config('updater_config')['updater_checks']

    queue = Lock("queue")
    if queue.is_locked:
        queue_data = yaml.load(queue.message)
        first_detection = False
    else:
        queue_data = {"items": []}
        first_detection = True

    notification = ""
    if first_detection:
        notification += "Restart scheduled ~{} minutes from now.\n".format(RESTART_DELAY)

    # Go through all checks and run functions from arm_manager, storing returned dict values
    # Return values must be dicts that will later be passed down to notification strings and action functions

    detected = False
    for check_id, check in enumerate(checks):
        if check_id not in queue_data['items']:
            check_response = getattr(am, check['check_function'])()
            if check_response:
                queue_data['items'][check_id] = check
                checks[check_id]['check_response'] = check_response
                log.debug("Adding to queue: {}; {};".format(check['update_name'], checks[check_id]['check_response']))
                notification += "{} detected, adding to queue.\n".format(check['update_name'].format(**checks[check_id]['check_response']))
                detected = True

    # Send notification if new update was detected regardless of whether it's first update or not.
    # If no updates detected it's not first detection, there's no queue and no notification will be sent.

    if detected and notification.strip():
        queue_data['update_time'] = datetime.now() + timedelta(minutes=RESTART_DELAY)
        queue.lock(yaml.dump(queue_data, default_flow_style=False))
        am.broadcast(notification, True)

    # Now check if datetime for scheduled restart is near. If not warn about upcoming update. If it is then start
    # performing restart and required actions.

    if queue.is_locked:
        if datetime.now() >= queue_data['update_time']:
            if auto_update:
                update(queue, queue_data)


def update(queue, queue_data):
    general = Lock()
    general.lock("Updating...")

    am.broadcast("Server restarts in 5 minutes!", True)
    time.sleep(60 * 4)
    am.broadcast("Server restart in 1 minute! Ready or not, here I come!")
    time.sleep(25)
    am.broadcast("Seriously, restarting now.")
    time.sleep(5)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    am.stop_server()

    for item_id, item_data in queue_data['items'].items():
        for action in item_data['actions']:
            try:
                result = getattr(am, action)(**item_data['check_response'])
            except Exception as e:
                am.broadcast("Unable to run {}: {}".format(action, str(e)))
                log.error("Unable to run {}: {}".format(action, str(e)), exc_info=True)

    am.start_server()
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    time.sleep(60 * 3)

    am.broadcast("Server should be back up and running by now or in a few more minutes.", True)

    general.unlock()
    queue.unlock()



# def update():
#     lock = Lock()
#
#     if lock.locked:
#         log.debug("Another script already running, exit...")
#         sys.exit()
#
#     if check_version():
#         print ("Update found!")
#         log.info("New version found, performing update.")
#         lock.lock("Game updater.")
#         run_with_delay(update_server, message="Update detected. ")
#         update_server()
#         time.sleep(10 * 60)
#         broadcast("Update finished. Server should be up and running by now.", True)
#         time.sleep(20 * 60)
#         lock.unlock()
#     else:
#         log.debug("No new versions found.")
#         print ("No new versions.")

if __name__ == "__main__":
    import sys

    general = Lock()
    if general.is_locked:
        sys.exit()

    perform_checks()