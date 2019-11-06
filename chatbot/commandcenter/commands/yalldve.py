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
        start = ["y","n","ny","wh","s",""]
        middle = ["all","would","could","can","whom","where","don","ain","yal","how"]
        end = ["n","t","st","ve","l","d"]

        slang = random.choice(start)
        if slang != "":
            slang += "'"
        slang += random.choice(middle)

        # guaranteed one ending
        slang += "'"
        slang += random.choice(end)
        
        # potentially infinite more
        while random.randint(1,2) < 2:
            slang += "'"
            slang += random.choice(end)

        return slang
