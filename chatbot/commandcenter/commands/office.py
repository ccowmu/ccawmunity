from ..command import Command
from ..eventpackage import EventPackage
import requests

# Talks to the office-presence container (same Docker compose network as the bot).

HELP_TEXT = """\
$office — shows who is physically in the CClub office (opt-in only).
Presence is tracked via DHCP leases on the morgana network (192.168.1.0/24).
Only registered devices are shown. Register yours to appear in the list.

Commands:
  $office              show who's in the office and how long they've been there
  $office help         show this message
  $office -r <mac>     register a MAC address to your Matrix username
  $office -d <mac>     deregister a MAC address from your Matrix username
  $office -l           list MAC addresses registered to your username

Finding your MAC address:
  Linux/macOS:  ip link   or   ifconfig
  Windows:      ipconfig /all
  Android/iOS:  Settings > Wi-Fi > tap your network > Advanced

MAC format: aa:bb:cc:dd:ee:ff  or  aa-bb-cc-dd-ee-ff
"""

class OfficeCommand(Command):
    def __init__(self):
        super().__init__()
        self.name = "$office"
        self.help = "$office | Shows who is in the CClub office | Usage: $office, $office help for full usage"
        self.author = "hellbacon and spacedog"
        self.last_updated = "February 2026"
        self.base_url = "http://office-presence:5001"

    def query(self, endpoint, data=None):
        endpoint = endpoint.lstrip("/")
        full_url = "{}/{}".format(self.base_url, endpoint)
        if data:
            return requests.post(full_url, data=data)
        else:
            return requests.get(full_url)

    def run(self, event_pack: EventPackage):
        r = ""
        nick = event_pack.sender.split(":")[0][1:]  # strip leading @ and :cclub.cs.wmich.edu

        if len(event_pack.body) == 3:
            if event_pack.body[1] == "-r":
                mac = event_pack.body[2]
                text = self.query("reg", {"nick": nick, "mac": mac}).text
                if text == "success":
                    r = "Successfully registered!"
                else:
                    r = "Something went wrong! Check that the MAC is valid and not already registered."
            elif event_pack.body[1] == "-d":
                mac = event_pack.body[2]
                text = self.query("dereg", {"nick": nick, "mac": mac}).text
                if text == "success":
                    r = "Successfully deregistered!"
                else:
                    r = "Something went wrong! Make sure that MAC is registered to your username."
        elif len(event_pack.body) == 2:
            if event_pack.body[1] == "-l":
                text = self.query("list", {"nick": nick}).text
                if text == "failure":
                    r = "No MAC addresses registered for: " + nick
                else:
                    r = text
            elif event_pack.body[1] == "help":
                r = HELP_TEXT
        else:
            r = self.query("plain").text
            if not r.strip():
                r = "Nobody is at Club... :("

        return r
