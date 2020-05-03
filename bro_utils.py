import re
import os
from paths import APP_DIR


import os, shutil
def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)

def get_real_ip(request):
    try:
        if request.headers.getlist("X-Forwarded-For"):
            ip = request.headers.getlist("X-Forwarded-For")[0]
        elif request.headers.getlist("X-Real-Ip"):
            ip = request.headers.getlist("X-Real-Ip")[0]
        else:
            ip = request.remote_addr
        return ip
    except:
        return "0.0.0.0"


def camelCaseSplit(text):
    """
    This function splits camel case into separate words
    :param text: Input text
    :return: array of words
    """
    matches = re.finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', text)
    return [m.group(0) for m in matches]


def get_available_submodules(path):
    '''
    :param path: import path for the parent module a.b separated with dots
    '''
    parts = path.split(".")
    filepath = os.path.join(APP_DIR, *parts)
    files = os.listdir(filepath)
    modules = []
    for f in files:
        name, ext = os.path.splitext(f)
        if ext.lower() == ".py":
            if not name.startswith("__") and not name.endswith("__"):
                if name.lower() != "base":
                    modules.append(path + "." + name)
    return modules


def sizeof_fmt(filepath, suffix='B'):
    num = os.stat(filepath).st_size
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


import os
from datetime import datetime, timedelta
import json
def json_loads(s):
    return json.loads(s)

#TODO

def calc_percent(i, total, max=100):
    return int(i / total * max)


class ProgressBar():
    def __init__(self, total, max=100, every=1):
        self.every = every
        self.max = max
        self.value = 0
        self.total=total
        self.eta = None
        self.last_time = datetime.now()
        self.timedelta_sum = datetime.now()-self.last_time

        print("[{}{}] ({}\{}) ETA: {}\n".format(
            "*" * 1,
            "." * (self.max - 1),
            self.value,
            self.total,
            self.eta
        ))

    def set_max(self, value):
        self.max = value

    def set_total(self, total):
        self.total=total

    def step(self, value=1):
        self.value += value
        if self.value % self.every == 0:
            perc = calc_percent(self.value, self.total, self.max)

            self.timedelta_sum += datetime.now()-self.last_time
            self.last_time = datetime.now()
            time_avg = self.timedelta_sum/self.value
            self.eta = time_avg*(self.total-self.value)

            os.system('cls')
            print("[{}{}] ({}\{}) ETA: {}\n".format(
                "*" * perc,
                "." * (self.max - perc),
                self.value,
                self.total,
                self.eta
            ))






def progress_bar(i, total, max=100):
    os.system('cls')
    perc = calc_percent(i, total, max)
    print("[{}{}] ({}\{})\n".format(
        "*" * perc,
        "." * (max - perc),
        i,
        total
    ))
    # print (perc, max-perc)