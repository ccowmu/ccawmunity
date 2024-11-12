from ..command import Command
from ..eventpackage import EventPackage
import requests
import json

class LetMeInCommand(Command):
    def __init__(self):
        super().__init__()
        self.name = "$letmein"
        self.help = "$letmein | Unlocks the door for club members"
        self.author = "Krackentosh"
        self.last_updated = "November 11th 2024"

    def run(self, event_pack: EventPackage):
        # Send a request to the remote server to trigger the door unlock
        try:
            data = {
                "status": {
                    "letmein": True
                }
            }
            response = requests.post("http://cclub.cs.wmich.edu:8878", data=json.dumps(data))
            
            if response.status_code == 200:
                return "Door is unlocking..."
            else:
                return "Failed to unlock the door. Server error."

        except Exception as e:
            print(f"Error sending request: {e}")
            return "An error occurred while attempting to unlock the door."
