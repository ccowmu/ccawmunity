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
        self.last_updated = "November 11th 2024"

    def run(self, event_pack: EventPackage):
        # Check if the command is used correctly
        if len(event_pack.body) < 1:
            return "Usage: $letmein"

        # Send a POST request to the server to unlock the door
        try:
            data = {
                "status": {
                    "letmein": True
                }
            }
            response = requests.post("http://dot.cs.wmich.edu:8878", data=json.dumps(data))

            # Check server response
            if response.status_code == 200:
                result_message = "Door is unlocking..."
                print(result_message)
                
                # Wait for 8 seconds before resetting
                time.sleep(8)

                # Reset letmein status to False
                data_reset = {
                    "status": {
                        "letmein": False
                    }
                }
                reset_response = requests.post("http://dot.cs.wmich.edu:8878", data=json.dumps(data_reset))

                if reset_response.status_code == 200:
                    return "Door is now locked again."
                else:
                    return "Failed to reset door status."

            else:
                return f"Failed to unlock the door. Server returned status code {response.status_code}."

        except Exception as e:
            print(f"Error sending request: {e}")
            return "An error occurred while attempting to unlock the door."
