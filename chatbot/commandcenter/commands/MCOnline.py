from ..command import Command
from ..eventpackage import EventPackage
import requests
import json

# note: this command only works when run on a machine in same subnet as dot.
# (this command will work when run on dot.)

class MCOnlineCommand(Command):
    def __init__(self):
        self.name = "$MCOnline"
        self.help = "$MCOnline | Tells who is online on the minecraft server"
        self.author = "presto"
        self.last_updated = "October 4th 2019"

    def run(self, event_pack: EventPackage):
        r = requests.get("https://mcapi.us/server/status?ip=dot.cs.wmich.edu&port=6969")
        status = json.loads(r)
        output = status["players"]
        # fp = open('/opt/app/logs/latest','r')
        # output = ""

        # line = fp.readline()
        # cnt = 1

        # while line:
        #     line = line.strip()
        #     if line.find("logged in"):
        #         output += line

        #     elif line.find("left the game"):
        #         output += line

        #     line = fp.readline()
        #     cnt += 1

        # fp.close()

        return output
