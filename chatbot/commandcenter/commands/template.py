# this file serves as a quick reference for the structure of a custom command class.

# import the Command parent class, and the EventPackage class.
from ..command import Command
from ..eventpackage import EventPackage

# create a class that inherits from Command
class TemplateCommand(Command):
    # set the name and author of the command inside of its constructor.
    def __init__(self):
        super().__init__() # this is necessary in order to initialize optional attributes with default values

        self.name = "$template" # this is required in order for the command to run!
        
        # define what will be shown when someone calls "help $<your command>"
        self.help = "$template | A template class for LEARNING PURPOSES ONLY. Do not run this command. Or else."
        
        self.author = "spacedog"
        self.last_updated = "Sept 28, 2018"

    # define what the command does here.
    # this function must return a string. the string will be sent to the room.
    def run(self, event_pack: EventPackage):
        return "I'm so dissapointed in you, " + event_pack.sender + "."
