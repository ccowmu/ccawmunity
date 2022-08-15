from ..command import Command
from ..eventpackage import EventPackage
from .img_api_key import API_KEY

import requests
import json
import random

class ImgCommand(Command):
    def __init__(self):
        super().__init__()
        self.name = "$img" # this is required in order for the command to run!
        
        # define what will be shown when someone calls "help $<your command>"
        self.help = "$img | $img <number> or just $img. Look up an IMG_0000 video on Youtube."
        
        self.author = "spacedog"
        self.last_updated = "Nov 11, 2020"

    # define what the command does here.
    # this function must return a string. the string will be sent to the room.
    def run(self, event_pack: EventPackage):
        num = random.randint(0, 1000)

        if len(event_pack.body) <= 2:
            try:
                num = int(event_pack.body[1])
            except:
                pass

        params = {
            "part" : "snippet",
            "q" : f"IMG_{num:04}",
            "key" : API_KEY,
            "maxResults" : "256"
        }

        r = requests.get('https://youtube.googleapis.com/youtube/v3/search', params=params)

        if "items" not in r.json():
            return "Error with Youtube API request. :("

        if r.json()["items"]:
            item = random.choice(r.json()["items"])

            title = item["snippet"]["title"]
            fulldesc = item["snippet"]["description"]
            desc = fulldesc if len(fulldesc) < 80 else fulldesc[:80] + "..."
            url = "https://youtube.com/watch/" + item["id"]["videoId"]

            return title + ", " + desc + ": " + url
        else:
            return "(No results)"
