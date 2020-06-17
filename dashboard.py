#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
import eventlet

eventlet.monkey_patch()

import os

from flask import Flask, Response, render_template, Markup, request, redirect
from flask_socketio import SocketIO
import traceback

import bro_utils

from ark_manager import *
from dbo import *
from jinja_filters import html_line_breaks
from configuration import version



realPath = os.path.dirname(os.path.realpath(__file__))
rp = realPath

app = Flask(__name__)
app.config['SECRET_KEY'] = 'kdFJDLGh@#@$@$e502983tuj#$g324'

socketio = SocketIO(app, async_mode='eventlet')





app.jinja_env.filters['html_line_breaks'] = html_line_breaks


# app.jinja_env.globals.update()

# app.jinja_env.filters['bbcode'] = utils.render_bbcode


@app.context_processor
def inject_global_variables():
    return dict(
        GetData=GetData(),
        getdata=getdata,
        n_to_br=html_line_breaks,
        server=server,
        version=version
    )


def add_background_task(task, interval):
    def tsk():
        while True:
            try:
                log.debug(f"Running background task {task.__name__}...")
                task()
                log.debug(f"Completed background task {task.__name__}!")
            except Exception as e:
                log.error(f"Can't run background task '{task.__name__}': {e}", exc_info=True)
            socketio.sleep(interval)

    socketio.start_background_task(tsk)


if __name__ == '__main__':
    from background_tasks import log_chat, log_gamelog, patreon_payout, log_chat_gamelog_ordered

    add_background_task(log_chat_gamelog_ordered, 10)
    # add_background_task(patreon_payout, 3600)

    from dashboard_views import app as dashboard_views
    from dashboard_api import app as api

    app.register_blueprint(dashboard_views)
    app.register_blueprint(api)

    try:
        log.info("Dashboard starting at port 1117...")
        socketio.run(app, debug=False, host='0.0.0.0', port=1117)
    except:
        log.error("Unable to start", exc_info=True)
