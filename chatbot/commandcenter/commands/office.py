from ..command import Command
from ..eventpackage import EventPackage
import requests

class OfficeCommand(Command):
    def __init__(self):
        self.name = "$office"
        self.help = "$office | Lists registered and unregistered devices on the CClub room network | Usage: $office"
        self.author = "hellbacon"
        self.last_updated = "April 20th 2019"

    def run(self, event_pack: EventPackage):
        return requests.get("141.218.118.171:5001/plain")

