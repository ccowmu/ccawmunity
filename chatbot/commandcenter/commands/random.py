from ..command import Command
from ..eventpackage import EventPackage

import random

class RandomCommand(Command):
    def __init__(self):
        super().__init__()
        self.name = "$random"
        self.help = "$random | Gets a random integer within a range (inclusive). | Usage: $random 1 10"
        self.author = "spacedog"
        self.last_updated = "Sept. 28, 2018"

    def run(self, event_pack: EventPackage):
        if len(event_pack.body) < 3:
            return "Invalid usage of $random (not enough arguments). usage: $random <low> <high>"
        floor = int(event_pack.body[1])
        ceiling = int(event_pack.body[2])
        return str(random.randint(floor, ceiling))
