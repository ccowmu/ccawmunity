from ..command import Command
from ..eventpackage import EventPackage
import requests

# note: this command only works when run on a machine in same subnet as dot.
# (this command will work when run on dot.)

class MCOnlineCommand(Command):
    def __init__(self):
        self.name = "$inspire"
        self.help = "$inspire | Posts an inspirational image"
        self.author = "presto"
        self.last_updated = "November 22nd 2019"

    def run(self, event_pack: EventPackage):
        r = requests.get("https://inspirobot.me/api?generate=true")
        return r.text