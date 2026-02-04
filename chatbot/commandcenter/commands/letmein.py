from ..command import Command
from ..eventpackage import EventPackage
import requests
from os import environ

class LetMeInCommand(Command):
    def __init__(self):
        super().__init__()
        self.name = "$letmein"
        self.help = "$letmein | Unlocks the door for club members"
        self.author = "Lochlan McElroy"
        self.last_updated = "February 2nd 2026"
        self.yakko_url = environ.get("YAKKO_URL", "")
        self.yakko_api_key = environ.get("YAKKO_API_KEY", "")

    def run(self, event_pack: EventPackage):
        if not self.yakko_url or not self.yakko_api_key:
            return "Error: YAKKO_URL or YAKKO_API_KEY environment variable is not set."

        if len(event_pack.body) < 1:
            return "Usage: $letmein"

        headers = {"Authorization": "Bearer " + self.yakko_api_key}

        try:
            # Send a POST request to unlock the door
            data = {
                "status": {
                    "letmein": True
                }
            }
            response = requests.post(
                self.yakko_url,
                json=data,
                headers=headers,
                timeout=5,
            )

            if response.status_code == 200:
                return "Door unlocked and now locked again."

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
