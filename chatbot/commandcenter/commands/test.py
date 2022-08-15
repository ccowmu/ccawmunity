from ..command import Command
from ..eventpackage import EventPackage

class TestCommand(Command):
    def __init__(self):
        super().__init__()
        self.name = "$test"
        self.help = "$test | No parameters requirerd, yells at dolphin."
        self.author = "strongth"
        self.last_updated = "Sept. 28, 2018"

    def run(self, event_pack: EventPackage):
        return "Why would have a test command DOLPHIN?"
