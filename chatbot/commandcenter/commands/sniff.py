from ..command import Command
from ..eventpackage import EventPackage

# Example of a "nosy" command that "sniffs" every message sent

class SniffCommand(Command):
    def __init__(self):
        self.name = "$sniff"
        self.help = "$sniff | I'm sniffing you."
        self.author = "spacedog"
        self.last_updated = "Oct. 2 2021"

        # set to true to have the bot call sniff_message on every message
        self.is_nosy = True
        
        self.last_sniffed = "..."

    def run(self, event_pack: EventPackage):
        return f"I smell... \"{self.last_sniffed}\"."

    def sniff_message(self, event_pack: EventPackage):
        self.last_sniffed = " ".join(event_pack.body)
