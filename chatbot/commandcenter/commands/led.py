from ..command import Command
from ..eventpackage import EventPackage
import requests
import re
import json

# note: this command only works when run on a machine in same subnet as dot.
# (this command will work when run on dot.)

class LedCommand(Command):
    def __init__(self):
        super().__init__()
        self.name = "$led"
        self.help = "$led | Changes leds in club. e.g. $led #00ff22 {color, chase, rainbow, or random}"
        self.author = "spacedog"
        self.last_updated = "February 14th 2020"

    def run(self, event_pack: EventPackage):
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

                requests.post("http://newyakko.cs.wmich.edu:8878", data=json.dumps(data))

        return r
