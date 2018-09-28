from ..command import Command
from ..eventpackage import EventPackage

import random

class RandomCommand(Command):
    def __init__(self):
        self.name = "$random"

    def run(self, event_pack: EventPackage):
        floor = int(event_pack.body[1])
        ceiling = int(event_pack.body[2])
        return str(random.randint(floor, ceiling))

    def get_help(self):
        return "$random - Gets a random integer within a range (inclusive). usage: $random 1 10"