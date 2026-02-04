from ..command import Command
from ..eventpackage import EventPackage
import requests
import re
from os import environ

# note: this command only works when run on a machine in same subnet as dot.
# (this command will work when run on dot.)

class LedCommand(Command):
    def __init__(self):
        super().__init__()
        self.name = "$led"
        self.help = "$led | Changes leds in club. e.g. $led #00ff22 {color, chase, rainbow, or random}"
        self.author = "spacedog"
        self.last_updated = "February 2nd 2026"
        self.yakko_url = environ.get("YAKKO_URL", "")
        self.yakko_api_key = environ.get("YAKKO_API_KEY", "")

    def run(self, event_pack: EventPackage):
        if not self.yakko_url or not self.yakko_api_key:
            return "Error: YAKKO_URL or YAKKO_API_KEY environment variable is not set."

        if len(event_pack.body) < 2:
            r = "Usage: $led #00ff22 {color, chase, rainbow, or random}"
        else:
            # try to read color
            color_string = event_pack.body[1]
            if re.match("^#[0-9 a-f A-F]{6}$", color_string) == None:
                r = "Invalid color."
            else:
                # valid color
                r = "Set color to: " + color_string
                red = int(color_string[1:3], 16)/2
                green = int(color_string[3:5], 16)/2
                blue = int(color_string[5:7], 16)/2

                data = {
                    "status": {
                        "red": red,
                        "green": green,
                        "blue": blue,
                    }
                }

                if len(event_pack.body) >= 3:
                    typ = event_pack.body[2]
                    if typ in ["color", "chase", "rainbow", "random"]:
                        data = {
                            "status": {
                                "red": red,
                                "green": green,
                                "blue": blue,
                                "type": typ
                            }
                        }
                        r += " ({})".format(typ)

                try:
                    response = requests.post(
                        self.yakko_url,
                        json=data,
                        headers={"Authorization": "Bearer " + self.yakko_api_key},
                        timeout=5,
                    )
                    if response.status_code != 200:
                        body_snip = (response.text or "").strip().replace("\n", " ")
                        if len(body_snip) > 200:
                            body_snip = body_snip[:200] + "..."
                        r += " (server {}: {})".format(response.status_code, body_snip)
                except Exception as e:
                    r += " (request failed: {})".format(e)

        return r
