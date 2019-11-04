from ..command import Command
from ..eventpackage import EventPackage

import random

class YalldveCommand(Command):
    def __init__(self):
        self.name = "$yalldve"
        self.help = "$yalldve | Slang generator"
        self.author = "presto"
        self.last_updated = "November 4th 2019"

    def run(self, event_pack: EventPackage):
        start=["y","n","ny","wh","s",""]
        middle=["all","would","could","can","whom","where","don","ain","yal"]
        end = ["n","t","st","ve","l","dve"]

        slang = start[random.randint(0, len(start)-1)]
        if slang != "":
            slang += "'"
        slang += middle[random.randint(0, len(middle)-1)]

        # guaranteed one ending
        slang += "'"
        slang += end[random.randint(0, len(end)-1)]
        
        # potentially infinite more
        while random.randint(1,2) < 2:
            slang += "'"
            slang += end[random.randint(0, len(end)-1)]

        return slang
