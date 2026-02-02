from ..command import Command
from ..eventpackage import EventPackage
import requests
import time

class LetMeInCommand(Command):
    def __init__(self):
        super().__init__()
        self.name = "$letmein"
        self.help = "$letmein | Unlocks the door for club members"
        self.author = "Lochlan McElroy"
        self.last_updated = "February 2nd 2026"

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
            response = requests.post(
                "http://yakko.cs.wmich.edu:8878",
                json=data,
                timeout=5,
            )

            if response.status_code == 200:
                # Wait briefly before resetting the status
                time.sleep(3)

                # Reset letmein status to False
                data_reset = {
                    "status": {
                        "letmein": False
                    }
                }
        
                reset_response = requests.post(
                    "http://yakko.cs.wmich.edu:8878",
                    json=data_reset,
                    timeout=5,
                )

                if reset_response.status_code == 200:
                    return "Door unlocked and now locked again."
                else:
                    return "Failed to reset door status."

            else:
                body_snip = (response.text or "").strip().replace("\n", " ")
                if len(body_snip) > 200:
                    body_snip = body_snip[:200] + "..."
                return (
                    "Failed to unlock the door. Server returned status code {}: {}."
                ).format(response.status_code, body_snip)

        except Exception as e:
            print("Error sending request: {}".format(e))
            return "An error occurred while attempting to unlock the door: {}.".format(e)
