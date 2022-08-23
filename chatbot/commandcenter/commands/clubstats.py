# this file serves as a quick reference for the structure of a custom command class.

# import the Command parent class, and the EventPackage class.
from ..command import Command
from ..eventpackage import EventPackage

# create a class that inherits from Command
class TemplateCommand(Command):
    # set the name and author of the command inside of its constructor.
    def __init__(self):
        self.name = "$clubstats" # this is required in order for the command to run!
        
        # define what will be shown when someone calls "help $<your command>"
        self.help = "$clubstats | A CLI for the clubstats data server. Please see $clubstats --help for more information "
        
        self.author = "acp"
        self.last_updated = "August 22, 2022"

        self.is_nosy = True


    # define what the command does here.
    # this function must return a string. the string will be sent to the room.
    def run(self, event_pack: EventPackage):
        return "Testing"

    def sniff_message(self, event_pack: EventPackage):
        self.last_sniffed = " ".join(event_pack.body)
