from ..command import Command
from ..eventpackage import EventPackage

class KarmaCommand(Command):
    def __init__(self):
        self.name = "$karma" # this is required in order for the command to run!
        self.help = "$karma | Display the karma of something. Usage: $karma <thing>"
        self.author = "spacedog"
        self.last_updated = "August 28, 2018"

    def run(self, event_pack: EventPackage):
        self.raw_db = True
        if len(event_pack.body) < 2:
            return "Usage: $karma <thing>"

        thing = " ".join(event_pack.body[1:]).lower()

        karma = self.db_get("karma:" + str(thing))
        
        if karma is not None:
            karma = karma.decode("utf-8")

        if karma is not None:
            return "Karma for \"{}\": {}".format(thing, karma)
        else:
            return "Karma for \"{}\": 0".format(thing)
