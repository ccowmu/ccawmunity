from ..command import Command
from ..eventpackage import EventPackage

# dummy classes of the built-in commands so that they are compatible with commands like $help or $info

class HelpCommand(Command):
    def __init__(self):
        self.name = "$help" # this is required in order for the command to run!
        self.help = "$help | Learn how to use commands. | Usage: $help or $help <command (including the $)>"
        self.author = "spacedog"
        self.last_updated = "Oct. 11, 2018"

    def run(self, event_pack: EventPackage):
        return "This command is built in to the commander. You should never see this text. Uh oh."

class InfoCommand(Command):
    def __init__(self):
        self.name = "$info" # this is required in order for the command to run!
        self.help = "$info | Display info about a command. | Usage: $info <command (including the $)>"
        self.author = "spacedog"
        self.last_updated = "Oct. 11, 2018"

    def run(self, event_pack: EventPackage):
        return "This command is built in to the commander. You should never see this text. Uh oh."