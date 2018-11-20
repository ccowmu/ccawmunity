from ..command import Command
from ..eventpackage import EventPackage

import botconfig

class PortCommand(Command):
    def __init__(self):
        self.name = "$port" # this is required in order for the command to run!
        
        self.help = "$port | Reports what port the bot's listeners are listening on."
        
        self.author = "spacedog"
        self.last_updated = "Nov 20, 2018"

    # define what the command does here.
    # this function must return a string. the string will be sent to the room.
    def run(self, event_pack: EventPackage):
        return "I'm listening on port " + str(botconfig.listener_port) + "."
