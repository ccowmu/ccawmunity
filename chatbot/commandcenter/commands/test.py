from ..command import Command
from ..eventpackage import EventPackage

class TestCommand(Command):
    def __init__(self):
        self.name = "$test"

    def run(self, event_pack: EventPackage):
        return "Why would have a test command DOLPHIN?"

    def get_help(self):
        return "$test - No parameters requirerd, yells at dolphin."