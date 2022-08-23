# this file serves as a quick reference for the structure of a custom command class.

# import the Command parent class, and the EventPackage class.
from ..command import Command
from ..eventpackage import EventPackage

# create a class that inherits from Command

sweardict = {
    "shit": 50,
    "fuck": 100,
    "ass": 25,
    "bitch": 25,
    "hell": 25,
    "damn": 25,
    "titties": 25,
    "tit": 25,
    "tits": 25,
    "titty": 25,
    "cunt": 150,
    "whore": 75,
    "slut": 25,
    "motherfucker": 150,
    "cock": 50,
    "dick": 50,
    "pussy": 50,
    "bussy": 75,
    "asshole": 50,
    "dumbass": 50,
    "clit": 75
}

penny = [
    "heck",
    "dang",
    "darn",
    "shucks",
    "shoot",
    "phooey",
    "crap",
    "butt",
    "booty",
    "butthole",
    "lintlicker"
]

class SwearjarCommand(Command):
    # set the name and author of the command inside of its constructor.
    def __init__(self):
        self.name = "$swearjar" # this is required in order for the command to run!
        
        # define what will be shown when someone calls "help $<your command>"
        self.help = "$swearjar | Learn how naughty someone is ;)."
        self.is_nosy = True
        
        self.author = "acp"
        self.last_updated = "August 10, 2022"

    # define what the command does here.
    # this function must return a string. the string will be sent to the room.
    def run(self, event_pack: EventPackage):
        return "I'm so dissapointed in you, " + event_pack.sender + "."

    def sniff_message(self, event_pack: EventPackage):
        self.last_sniffed = " ".join(event_pack.body)

        matches = regex.findall(message)

        for word in matches:
            