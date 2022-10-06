from ..command import Command
from ..eventpackage import EventPackage

import subprocess
import os

# create a class that inherits from Command
class GPT2Command(Command):
    # set the name and author of the command inside of its constructor.
    def __init__(self):
        super().__init__()
        self.name = "$gpt2" # this is required in order for the command to run!
        
        self.help = "$gpt2 | Complete text. usage: $gpt2 <starting text here>"
        
        self.author = "spacedog"
        self.last_updated = "Dec 5, 2020"

    # define what the command does here.
    # this function must return a string. the string will be sent to the room.
    def run(self, event_pack: EventPackage):
        if len(event_pack.body) >= 2:
            # put message text into single string
            seed = " ".join(event_pack.body[i] for i in range(1, len(event_pack.body)))
            
            # run gpt2
            path = os.path.dirname(os.path.realpath(__file__))
            p = subprocess.run(["./gpt2tc", "g", seed], capture_output=True, cwd=path + "/bin/gpt2tc/")
            string = p.stdout.decode("utf-8")

            # remove last few lines of statistics
            string = string[:string.rfind('\n')]
            string = string[:string.rfind('\n')]

            return string
        else:
            return "usage: $gpt2 <starting text here>"
