from .command import Command

class TestCommand(Command):
    def __init__(self):
        self.name = "$test"

    def run(self, body={}, roomId="", sender="", event={}):
        return "Why would have a test command DOLPHIN?"

    def getHelp(self):
        return "$test - No parameters requirerd, yells at dolphin."