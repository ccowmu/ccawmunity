from ..command import Command
from ..eventpackage import EventPackage
import requests
import json

# note: this command only works when run on a machine in same subnet as dot.
# (this command will work when run on dot.)

class MCOnlineCommand(Command):
    def __init__(self):
        super().__init__()
        self.name = "$MCOnline"
        self.help = "$MCOnline | Tells who is online on the minecraft server"
        self.author = "presto"
        self.last_updated = "October 4th 2019"

    def run(self, event_pack: EventPackage):
        r = requests.get("https://api.mcsrvstat.us/2/dot.cs.wmich.edu:6969")
        status = json.loads(r.content.decode("utf-8"))
        
        playerList = ""
        if status["players"]["online"] > 0:
            playerList = "Players Online: "
            plural = False
            for player in status["players"]["list"]:
                if plural:
                    playerList = playerList + ", "
                playerList = playerList + player
                plural = True

        else:
            playerList = "No one is online :("
        

        return playerList
