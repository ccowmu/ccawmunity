from ..command import Command
from ..eventpackage import EventPackage
import requests
import json
import threading
import time

class LetMeInCommand(Command):
    def __init__(self):
        super().__init__()
        self.name = "$letmein"
        self.help = "$letmein | Unlocks the door for club members"
        self.author = "Lochlan McElroy"
        self.last_updated = "November 11th 2024"

    def run(self, event_pack: EventPackage):
        if len(event_pack.body) < 1:
            return "Usage: $letmein"

        # Send a POST request to unlock the door
        try:
            data = {
                "status": {
                    "letmein": True
                }
            }
            response = requests.post("http://dot.cs.wmich.edu:8878", data=json.dumps(data))

            if response.status_code == 200:
                # Start a background thread to reset the status after 8 seconds
                threading.Thread(target=self.reset_letmein_status).start()
                return "Door is unlocking..."
            else:
                return f"Failed to unlock the door. Server returned status code {response.status_code}."

        except Exception as e:
            print(f"Error sending request: {e}")
            return "An error occurred while attempting to unlock the door."

    def reset_letmein_status(self):
        """Background thread function to reset letmein status after 8 seconds."""
        time.sleep(8)
        try:
            data_reset = {
                "status": {
                    "letmein": False
                }
            }
            reset_response = requests.post("http://dot.cs.wmich.edu:8878", data=json.dumps(data_reset))
            if reset_response.status_code == 200:
                print("Door status reset to locked.")
            else:
                print("Failed to reset door status.")
        except Exception as e:
            print(f"Error resetting status: {e}")
