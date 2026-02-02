from ..command import Command
from ..eventpackage import EventPackage
import requests
import json
import time

class LetMeInCommand(Command):
    def __init__(self):
        super().__init__()
        self.name = "$letmein"
        self.help = "$letmein | Unlocks the door for club members"
        self.author = "Lochlan McElroy"
        self.last_updated = "February 1st 2026"

    def run(self, event_pack: EventPackage):
        if len(event_pack.body) < 1:
            return "Usage: $letmein"

        try:
            # Send a POST request to unlock the door
            data = {
                "status": {
                    "letmein": True
                }
            }
            response = requests.post("http://newyakko.cs.wmich.edu:8878", data=json.dumps(data))

            if response.status_code == 200:
                # Wait for 5 seconds before resetting the status
                time.sleep(3)

                # Reset letmein status to False
                data_reset = {
                    "status": {
                        "letmein": False
                    }
                }
        
                reset_response = requests.post("http://newyakko.cs.wmich.edu:8878", data=json.dumps(data_reset))

                if reset_response.status_code == 200:
                    return "Door unlocked and now locked again."
                else:
                    return "Failed to reset door status."

            else:
                return f"Failed to unlock the door. Server returned status code {response.status_code}."

        except Exception as e:
            print(f"Error sending request: {e}")
            return "An error occurred while attempting to unlock the door."

