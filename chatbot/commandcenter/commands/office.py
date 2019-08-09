from ..command import Command
from ..eventpackage import EventPackage
import requests

# note: this command only works when run on a machine in same subnet as 141.218.118.171.
# (this command will work when run on dot.)

class OfficeCommand(Command):
    def __init__(self):
        self.name = "$office"
        self.help = "$office | Lists people connected to CClub network | Usage: $office, register: $office -r <mac>, deregister: $office -d <mac>"
        self.author = "hellbacon and spacedog"
        self.last_updated = "August 7th 2019"

    def run(self, event_pack: EventPackage):
        r = ""

        if len(event_pack.body) == 3:
            # command...
            if event_pack.body[1] == "-r":
                # register
                nick = event_pack.sender.split(":")[0][1:] # gets username without :cclub.cs.wmich.edu
                mac = event_pack.body[2]
                text = requests.post("http://141.218.118.171:5001/reg", data={"nick": nick, "mac": mac}).text
                if text == "success":
                    r = "Successfully registered!"
                else:
                    r = "Something went wrong!"
            elif event_pack.body[1] == "-d":
                # deregister
                nick = event_pack.sender.split(":")[0][1:] # gets username without :cclub.cs.wmich.edu
                mac = event_pack.body[2]
                text = requests.post("http://141.218.118.171:5001/dereg", data={"nick": nick, "mac": mac}).text
                if text == "success":
                    r = "Successfully deregistered!"
                else:
                    r = "Something went wrong!"
        else:
            # just a query
            r = requests.get("http://141.218.118.171:5001/plain").text
            
        return r
