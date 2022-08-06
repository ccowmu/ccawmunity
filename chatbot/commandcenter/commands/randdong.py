from ..command import Command
from ..eventpackage import EventPackage

import random
import math

class RandDong(Command):
    def __init__(self):
        self.name = "$randdong"
        
        self.help = "$randdong | Print an ASCII dong of random length"
        
        self.author = "bluebell"
        self.last_updated = "Aug. 5, 2022"

    def run(self, event_pack: EventPackage):
        dong_len = math.floor(random.lognormvariate(2.3,1))
        return "8" + dong_len * '=' + "D"
