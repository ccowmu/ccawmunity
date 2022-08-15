from ..command import Command
from ..eventpackage import EventPackage

# a simple command to demonstrate how to connect to redis

class CountCommand(Command):
    def __init__(self):
        super().__init__()
        self.name = "$count" # this is required in order for the command to run!
        self.help = "$count | Count for fun!"
        self.author = "spacedog"
        self.last_updated = "August 27, 2019"

    def run(self, event_pack: EventPackage):
        count = self.db_incr("i")
        return "We counted to {}!".format(count)
