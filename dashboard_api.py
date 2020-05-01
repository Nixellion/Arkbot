from flask import Blueprint, render_template, request, redirect, Response, jsonify
from ark_manager import *
from dbo import *
import functools
from locks import Lock

app = Blueprint("views", __name__)


def catch_errors(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            traceback.print_exc()
            return jsonify({"error": str(e), "traceback": traceback.format_exc()})
    return wrapped

@app.route("/api/serverchat", methods=['POST'])
@catch_errors
def server_chat():
    if request.method == "POST":
        message = request.form.get('message')
        # log.debug(f"message {message}")
        serverchat(message)
        return redirect("/")

@app.route("/api/get_chat")
@catch_errors
def get_chat():
    count = request.args.get('count', None)
    output = []
    if not count:
        messages = GameLog.select().where(GameLog.log_type == "chat")
    else:
        messages = GameLog.select().where(GameLog.log_type == "chat").limit(int(count))
    for message in messages:
        output.append(message.__dict__)
    return jsonify(output)


@app.route("/api/get_log")
@catch_errors
def get_log():
    count = request.args.get('count', None)
    log_type = request.args.get('type', None)
    output = []
    if log_type:
        if not count:
            messages = GameLog.select().where(GameLog.log_type == log_type).get()
        else:
            messages = GameLog.select().where(GameLog.log_type == log_type).limit(int(count)).get()
    else:
        if not count:
            messages = GameLog.select().get()
        else:
            messages = GameLog.select().limit(int(count)).get()
    for message in messages:
        output.append(message.__dict__)

    return jsonify(output)


@app.route("/api/get_players")
@catch_errors
def get_players():
        players = GetData().players
        output = []
        for player in players:
            output.append(player.__dict__)
        return jsonify(output)

@app.route("/api/server")
@catch_errors
def server_data():
        return jsonify(server.__dict__)

@app.route("/api/Get_Data/<attribute>")
@catch_errors
def get_data(attribute):
        if attribute == "all":
            output = GetData.__dict__
        else:
            output = GetData.__getattribute__(attribute)

        return jsonify(output)

@app.route("/api/unlock/<name>")
@catch_errors
def unlock(name):
    lock = Lock(name)
    lock.unlock()
    return Response(f"Lock {name} removed.")

@app.route("/api/arkbot_actions/", methods=["POST"])
@catch_errors
def arkbot_actions():
    if request.method == "POST":
        cmd = f"""su - arkserver -c 'python3 /home/arkserver/Arkbot/ark_{request.form["action"]}.py --message "{request.form["message"]}"'"""
        cmd_out = subprocess.check_output(cmd, shell=True).decode("utf-8")
        log.info(str(cmd_out))
        return Response(str(cmd_out))

@app.route("/api/linuxgsm_actions/", methods=["GET", "POST"])
@catch_errors
def linuxgsm_actions():
    if request.method == "POST":
        cmd = f"""su - arkserver -c '/home/arkserver/arkserver {request.form["action"]}'"""
        cmd_out = subprocess.check_output(cmd, shell=True).decode("utf-8")
        log.info(str(cmd_out))
        return Response(str(cmd_out))
    else:
        return Response("POST!!!")

@app.route("/api/check_update/")
@catch_errors
def check_update():
    return jsonify({"success":getdata.check_for_update()})

@app.route("/api/update/")
@catch_errors
def update():
    log.info("Update requested from git...")
    gitrepo.remotes.origin.pull()
    return redirect("/api/restart")

@app.route("/api/restart/")
@catch_errors
def restart():
    log.info("Restarting...")
    result = ""
    import subprocess
    command = 'service arkdashboard restart'
    log.info("Running:", command)
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    process.wait()
    result += str(process.returncode) + "\n\n<hr>"
    log.info(result)
    return redirect("/")
