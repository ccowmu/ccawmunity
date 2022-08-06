from ..command import Command
from ..command import CommandRainbowResponse
from ..eventpackage import EventPackage

import random
import math

class RandDong(Command):
    def __init__(self):
        self.name = "$rranddong"
        
        self.help = "$rranddong | Just like randdong, but more gay!"
        
        self.author = "bluebell"
        self.last_updated = "Aug. 6, 2022"

    def run(self, event_pack: EventPackage):
        dong_len = math.floor(random.lognormvariate(2.3,1))
        dong_str = "8" + dong_len * '=' + "D"
        return CommandRainbowResponse(dong_str)
