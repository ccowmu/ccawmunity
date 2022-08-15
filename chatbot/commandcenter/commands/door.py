from ..command import Command
from ..eventpackage import EventPackage
import requests

# note: this command only works when run on a machine in same subnet as dot.
# (this command will work when run on dot.)

class DoorCommand(Command):
    def __init__(self):
        super().__init__()
        self.name = "$door"
        self.help = "$door | Tells the status of the cclub office door"
        self.author = "sweeney and spacedog"
        self.last_updated = "October 3rd 2019"

    def run(self, event_pack: EventPackage):
        r = requests.get("http://dot.cs.wmich.edu:8877").text

        return r
