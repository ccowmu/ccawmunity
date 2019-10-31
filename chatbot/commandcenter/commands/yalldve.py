from ..command import Command
from ..eventpackage import EventPackage
import requests

import random

# note: this command only works when run on a machine in same subnet as dot.
# (this command will work when run on dot.)

class YalldveCommand(Command):
    def __init__(self):
        self.name = "$yalldve"
        self.help = "$yalldve | Slang generator"
        self.author = "presto"
        self.last_updated = "October 31st 2019"

    def run(self, event_pack: EventPackage):
        start=["y","n","ny"]
        middle=["all","would","could","can","whom","where","don","ain"]
        end = ["n","t","st","ve"]

        slang = start[random.randint(0, len(start)-1)]
        slang += "'"
        slang += middle[random.randint(0, len(middle)-1)]

        numEnds = random.randint(0,3)

        for i in range(0,numEnds):
            slang += "'"
            slang += end[random.randint(0, len(end)-1)]

        return slang
