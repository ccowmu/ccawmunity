import re

from ..command import Command
from ..eventpackage import EventPackage

# looks for "xyz++"
regex = re.compile(r"([^\-\$ ]+|(?:\().+?(?:\)))(\+\+|--)")

class KarmaCommand(Command):
    def __init__(self):
        super().__init__()
        self.name = "$karma" # this is required in order for the command to run!
        self.help = "$karma | Display the karma of something. Usage: $karma <thing>"
        self.author = "spacedog"
        self.last_updated = "Oct 2, 2021"

        self.is_nosy = True

    def run(self, event_pack: EventPackage):
        if len(event_pack.body) < 2:
            return "Usage: $karma <thing>"

        thing = " ".join(event_pack.body[1:]).lower()

        karma = self.db_get(str(thing))
        
        if karma is not None:
            karma = karma.decode("utf-8")

        if karma is not None:
            return "Karma for \"{}\": {}".format(thing, karma)
        else:
            return "Karma for \"{}\": 0".format(thing)

    def sniff_message(self, event_pack: EventPackage):
        message = " ".join(event_pack.body)
        matches = regex.findall(message)

        for tup in matches:
            key = tup[0]

            if key[0] == "(" and key[-1:] == ")":
                key = key[1:-1] # chop off parenthesis

            key = key.lower()
            op = tup[1]

            # keep a set of all items
            self.db_set_add("all_items", key)

            if op == "++":
                print(f"INFO | karma ++'d {key}")
                self.db_incr(str(key))
            elif op == "--":
                print(f"INFO | karma --'d {key}")
                self.db_incrby(str(key), -1)
