from ..command import Command
from ..eventpackage import EventPackage

import requests
import json

class TestListenersCommand(Command):
    def __init__(self):
        self.name = "$test_listeners"
        
        self.help = "$test_listeners | Tests if the listener functionality of the bot is functioning by sending a test POST request."
        
        self.author = "spacedog"
        self.last_updated = "Nov 16, 2018"

    def run(self, event_pack: EventPackage):

        requests.post("http://localhost:5170", json={"type":"test"})

        return "Sent test."
