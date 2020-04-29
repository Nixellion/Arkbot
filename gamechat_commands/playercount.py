from gamechat_commands import BaseSkill
from ark_manager import serverchat, listplayers

class Skill(BaseSkill):

    def process(self, data):
        players = listplayers()
        if players:
            serverchat(f"There are {len(players)} players on the server.")