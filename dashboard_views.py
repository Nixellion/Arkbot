from flask import Blueprint, render_template, request
from debug import catch_errors_json
from locks import get_locks
from dbo import *



app = Blueprint("dashboard_views", __name__)



@app.route("/")
@catch_errors_json
def index():
    return render_template("index.html", locks=get_locks())


@app.route("/gamelog")
@catch_errors_json
def gamelog():
    limit = request.args.get("limit", 150)
    return render_template("gamelog.html", limit=limit)

@app.route("/dashlog")
@catch_errors_json
def dashlog():
    return render_template("dashlog.html")


@app.route("/server_control")
@catch_errors_json
def server_control():
    return render_template("server_controls.html")