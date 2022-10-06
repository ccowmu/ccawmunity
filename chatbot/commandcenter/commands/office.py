from ..command import Command
from ..eventpackage import EventPackage
import requests

# note: this command only works when run on a machine in same subnet as 141.218.118.171.
# (this command will work when run on dot.)

class OfficeCommand(Command):
    def __init__(self):
        super().__init__()
        self.name = "$office"
        self.help = "$office | Lists people connected to CClub network | Usage: $office, register: $office -r <mac>, deregister: $office -d <mac>, list your macs: $office -l"
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
                text = requests.post("http://141.218.117.49:5001/reg", data={"nick": nick, "mac": mac}).text
                if text == "success":
                    r = "Successfully registered!"
                else:
                    r = "Something went wrong!"
            elif event_pack.body[1] == "-d":
                # deregister
                nick = event_pack.sender.split(":")[0][1:] # gets username without :cclub.cs.wmich.edu
                mac = event_pack.body[2]
                text = requests.post("http://141.218.117.49:5001/dereg", data={"nick": nick, "mac": mac}).text
                if text == "success":
                    r = "Successfully deregistered!"
                else:
                    r = "Something went wrong!"
        elif len(event_pack.body) == 2:
            if event_pack.body[1] == "-l":
                # list users mac
                nick = event_pack.sender.split(":")[0][1:] # gets username without :cclub.cs.wmich.edu
                text = requests.post("http://141.218.117.49:5001/list", data={"nick": nick}).text
                if text == "failure":
                    r = "There are no mac addresses registed for the username: " + nick
                else:
                    r = text
        else:
            # just a query
            r = requests.get("http://141.218.117.49:5001/plain").text
            if not r.strip(): # empty response, noone is in the office.
                r = "Noone is at Club... :("


        return r
