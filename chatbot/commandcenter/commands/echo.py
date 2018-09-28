from ..command import Command
from ..eventpackage import EventPackage

class EchoCommand(Command):
    def __init__(self):
        self.name = "$echo"
        self.help = "$echo | N parameters accepted separated by spaces, bot echoes them back to chat. | Usage: $echo arg1 arg2"
        self.author = "strongth"
        self.last_updated = "Sept. 28, 2018"

    def run(self, event_pack: EventPackage):
        if(len(event_pack.body) >= 2):
            output = " ".join(event_pack.body[i] for i in range(1, len(event_pack.body)))
            return output
        else:
            return "Needs more arguments, for example - \"$echo test\""
