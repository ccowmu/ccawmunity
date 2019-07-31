from ..command import Command
from ..eventpackage import EventPackage
import requests

# note: this command only works when run on a machine in same subnet as 141.218.118.171.
# (this command will work when run on dot.)

class OfficeCommand(Command):
    def __init__(self):
        self.name = "$office"
        self.help = "$office | Lists registered and unregistered devices on the CClub room network | Usage: $office"
        self.author = "hellbacon"
        self.last_updated = "April 20th 2019"

    def run(self, event_pack: EventPackage):
        resp = requests.get("http://141.218.118.171:5001/json")
        return resp.text
