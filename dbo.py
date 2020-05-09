# region ############################# IMPORTS #############################
# endregion
# region ############################# IMPORTS #############################



import os
import traceback
from datetime import datetime, date
import sys
from peewee import *
from ark_manager import *
from paths import APP_DIR, DATABASE_PATH

from git import Repo as GitRepo

from pprint import PrettyPrinter

# endregion

pp = PrettyPrinter(indent=4)

# region ############################# GLOBALS #############################

db_path = DATABASE_PATH
db = SqliteDatabase(db_path)

# endregion
CHAT_LOG_PATH = os.path.join(APP_DIR, "chatlog.txt")
GAME_LOG_PATH = os.path.join(APP_DIR, "gamelog.txt")



gitrepo = GitRepo.init(APP_DIR)
assert not gitrepo.bare

class GetData():
    def get_chat_log(self, limit=30):
        try:
            return GameLog.select().where(
                (GameLog.log_type == log_types.index("chat")) | (GameLog.log_type == log_types.index("serverchat"))).order_by(GameLog.id.desc()).limit(limit)
        except:
            log.warning(traceback.format_exc())
            return "No records yet or database error."

    def get_game_log(self, limit=30):
        try:
            return GameLog.select().order_by(GameLog.id.desc()).limit(limit)
        except:
            log.warning(traceback.format_exc())
            return "No records yet or database error."

    @property
    def dashlog(self):
        with open(os.path.join(APP_DIR, "dashboard_info.log"), "r") as f:
            return f.read()

    @property
    def chat_log(self):
        try:
            return GameLog.select().where(
                (GameLog.log_type == log_types.index("chat")) | (GameLog.log_type == log_types.index("serverchat")))
        except:
            log.warning(traceback.format_exc())
            return "No records yet or database error."

    @property
    def game_log(self):
        try:
            return GameLog.select()
        except:
            log.warning(traceback.format_exc())
            return "No records yet or database error."

    @property
    def players(self):
        return listplayers()

    @property
    def git_commit(self):
        return gitrepo.heads.master.commit

    def log_id_text(self, id):
        return log_types[id]

    def check_for_update(self):
        fetch_info = gitrepo.remotes.origin.fetch()[0]

        return gitrepo.heads.master.commit != fetch_info.commit

getdata = GetData()

# region ############################# TABLE CLASSES #############################
class BroModel(Model):
    date_created = DateTimeField(default=datetime.now())
    date_updated = DateTimeField(default=datetime.now())
    date_deleted = DateTimeField(null=True)
    deleted = BooleanField(default=False)

    def mark_deleted(self):
        self.deleted = True
        self.date_deleted = datetime.now()
        self.save()


class GPSLog(BroModel):
    class Meta:
        database = db

    lat = FloatField(null=False)
    lon = FloatField(null=False)


log_types = [
    "killed_by_wild",
    "join",
    "leave",
    "killed_by_tribe",
    "chat",
    "tame",
    "claim",
    "starve",
    "destruction",
    "demolish",
    "serverchat",
    "killself",
    "tame_killed_by_wild",
    "tame_killed_by_tribe",
    "tame_claim"
]

log_regexps = {
    "killed_by_wild": "(?P<datetime>.*): Tribe (?P<player_tribe>.*), ID (?P<player_tribe_id>.*): Day (?P<day>.*), (?P<daytime>.*): Tribemember (?P<player>.*) - Lvl (?P<player_lvl>.*) was killed by (a|an) (?P<killer>.*) - Lvl (?P<killerlvl>.*)!\)",
    "join": "(?P<datetime>.*): (?P<player>.*) joined this ARK!",
    "leave": "(?P<datetime>.*): (?P<player>.*) left this ARK!",
    "killed_by_tribe": ["(?P<datetime>.*): Tribe (?P<player_tribe>.*), ID (?P<player_tribe_id>.*): Day (?P<day>.*), (?P<daytime>.*): Tribemember (?P<player>.*) - Lvl (?P<player_lvl>.*) was killed by (?P<killer>.*) - Lvl (?P<killerlvl>.*) \((?P<killer_tribe>.*)\)!\)",
                        '''(?P<datetime>.*): Tribe (?P<player_tribe>.*), ID (?P<player_tribe_id>.*): Day (?P<day>.*), (?P<daytime>.*): Your (?P<tame>) - Lvl (?P<tame_lvl>.*) ((?P<tame_tribe>)) was killed by (?P<killer>.*) - Lvl (?P<killerlvl>.*) \((?P<killer_tribe>.*)\)!\)'''],
    "chat": "(?P<datetime>.*): (?P<player>.*) \((?P<player_tribe>.*)\): (?P<message>.*)",
    "tame": "(?P<datetime>.*): Tribe (?P<player_tribe>.*), ID (?P<player_tribe_id>.*): Day (?P<day>.*), (?P<daytime>.*): (?P<player>.*) Tamed (a|an) (?P<tame>.*) - Lvl (?P<tame_lvl>.*) \((?P<tame_tribe>.*)\)!\)",
    "claim": "(?P<datetime>.*): Tribe (?P<player_tribe>.*), ID (?P<player_tribe_id>.*): Day (?P<day>.*), (?P<daytime>.*): (?P<player>.*) Claimed '(?P<tame>.*) - Lvl (?P<tame_lvl>.*) \((?P<tame_tribe>.*)\)'!\)",
    "starve": "(?P<datetime>.*): Tribe (?P<player_tribe>.*), ID (?P<player_tribe_id>.*): Day (?P<day>.*), (?P<daytime>.*): (?P<tame>.*) - Lvl (?P<tame_lvl>.*) starved to death!\)",
    "destruction": "(?P<datetime>.*): Tribe (?P<player_tribe>.*), ID (?P<player_tribe_id>.*): Day (?P<day>.*), (?P<daytime>.*): Your '(?P<structure>.*)' was destroyed!\)",
    "demolish": "(?P<datetime>.*): Tribe (?P<player_tribe>.*), ID (?P<player_tribe_id>.*): Day (?P<day>.*), (?P<daytime>.*): (?P<player>.*) demolished a '(?P<structure>.*)'!\)",
    "serverchat": "(?P<datetime>.*): SERVER: (?P<message>.*)",
    "killself": "(?P<datetime>.*): Tribe (?P<player_tribe>.*), ID (?P<player_tribe_id>.*): Day (?P<day>.*), (?P<daytime>.*): Tribemember (?P<player>.*) - Lvl (?P<player_lvl>.*) was killed!\)",
    "tame_killed_by_wild": "(?P<datetime>.*): Tribe (?P<player_tribe>.*), ID (?P<player_tribe_id>.*): Day (?P<day>.*), (?P<daytime>.*): Your (?P<tame>.*) - Lvl (?P<tame_lvl>.*) was killed by (a|an) (?P<killer>.*) - Lvl (?P<killerlvl>.*)!\)",
    "tame_killed_by_tribe": "(?P<datetime>.*): Tribe (?P<player_tribe>.*), ID (?P<player_tribe_id>.*): Day (?P<day>.*), (?P<daytime>.*): Your (?P<tame>.*) - Lvl (?P<tame_lvl>.*) \((?P<tame_tribe>.*)\) was killed by (?P<killer>.*) - Lvl (?P<killerlvl>.*) \((?P<killer_tribe>.*)\)!\)",
    "tame_claim": "(?P<datetime>.*): Tribe (?P<player_tribe>.*), ID (?P<player_tribe_id>.*): Day (?P<day>.*), (?P<daytime>.*): (?P<player>.*) claimed '(?P<tame>.*) - Lvl (?P<tame_lvl>.*) \((?P<tame_tribe>.*)\)'!\)"
}


class GameLog(BroModel):
    raw = TextField()
    time = DateTimeField(null=True)
    daytime = CharField(null=True)
    log_type = IntegerField()
    day = IntegerField(null=True)
    player = CharField(null=True)
    player_lvl = IntegerField(null=True)
    player_tribe = CharField(null=True)
    player_tribe_id = IntegerField(null=True)
    killer = CharField(null=True)
    killer_lvl = IntegerField(null=True)
    killer_tribe = CharField(null=True)
    tame = CharField(null=True)
    tame_lvl = CharField(null=True)
    tame_tribe = CharField(null=True)
    structure = CharField(null=True)
    message = TextField(null=True)

    class Meta:
        database = db


def filterout_richtext(line):
    filterout = ['<RichColor Color="1, 0, 0, 1">', '<RichColor Color="0, 1, 0, 1">', '</>', '<RichColor Color="1, 1, 0, 1">']
    for fo in filterout:
        line = line.replace(fo, '')
    return line

def store_log_data(line):
    try:
        if line.strip():
            line = filterout_richtext(line)
            gl = GameLog()
            gl.raw = line
            for logtype, regexes in log_regexps.items():
                if isinstance(regexes, list):
                    for regex in regexes:
                        match = re.match(regex, line)
                        if match:
                            # print (logtype, match.groupdict())
                            data = match.groupdict()
                            break
                    if match:
                        break
                else:
                    regex = regexes
                    match = re.match(regex, line)
                    if match:
                        # print (logtype, match.groupdict())
                        data = match.groupdict()
                        break

            if not match:
                log.debug(f"No matches found in regexes for {line}")
                return None
            timestamp = data.get("datetime")
            if timestamp:
                timestamp = datetime.strptime(timestamp, "%Y.%m.%d_%H.%M.%S")
            gl.time = timestamp
            gl.log_type = log_types.index(logtype)
            day = data.get("day")
            gl.daytime = data.get("daytime")
            if day:
                gl.day = int(day)
            gl.player = data.get("player")
            gl.player_lvl = data.get("player_lvl")
            gl.player_tribe = data.get("player_tribe")
            gl.player_tribe_id = data.get("player_tribe_id")
            gl.killer = data.get("killer")
            gl.killer_lvl = data.get("killer_lvl")
            gl.killer_tribe = data.get("killer_tribe")
            gl.tame = data.get("tame")
            gl.tame_lvl = data.get("tame_lvl")
            gl.tame_tribe = data.get("tame_tribe")
            gl.structure = data.get("structure")
            gl.message = data.get("message")
            log.debug(f"Saving {gl.__dict__}")
            gl.save()
            return gl
    except Exception as e:
        log.error(f"Could not parse log string: {line}; {str(e)}")
        return None


class PlayerRecord(BroModel):
    class Meta:
        database = db

    player_id = CharField(null=False, unique=True)
    steam_id = CharField(null=False)
    username = BooleanField(default=False)
    movements = ForeignKeyField(GPSLog, backref="player")


do_migrate = False
if do_migrate:
    print("=====================")
    print("Migration stuff...")
    try:
        from playhouse.migrate import *

        migrator = SqliteMigrator(db)

        telegram_chat_id = CharField(null=True)
        telegram_active = BooleanField(null=True)
        telegram_last_sent = DateTimeField(null=True)

        migrate(
            migrator.add_column('person', 'telegram_chat_id', telegram_chat_id),
            migrator.add_column('person', 'telegram_active', telegram_active),
            migrator.add_column('person', 'telegram_last_sent', telegram_last_sent)
        )
        print("Migration success")
        print("=====================")
    except:
        traceback.print_exc()
        print("=====================")

db.connect()
db.create_tables([PlayerRecord, GPSLog, GameLog])

# endregion
