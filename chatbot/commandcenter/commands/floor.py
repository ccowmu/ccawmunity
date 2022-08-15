from ..command import Command
from ..eventpackage import EventPackage
import requests

# note: this command only works when run on a machine in same subnet as dot.
# (this command will work when run on dot.)

class FloorCommand(Command):
    def __init__(self):
        super().__init__()
        self.name = "$floor"
        self.help = "$floor | Tells the status of the cclub office floor"
        self.author = "presto"
        self.last_updated = "October 25th 2019"

    def run(self, event_pack: EventPackage):

        return "Hmm, yes, the floor here is made out of floor."
