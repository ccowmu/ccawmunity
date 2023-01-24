# this file serves as a quick reference for the structure of a custom command class.

# import the Command parent class, and the EventPackage class.
from ..command import Command
from ..eventpackage import EventPackage
import requests
import json
from botconfig import clubstats_endpoint

# create a class that inherits from Command
class ClubstatsCommand(Command):
    # set the name and author of the command inside of its constructor.
    def __init__(self):
        super().__init__()
        self.name = "$clubstats" # this is required in order for the command to run!
        
        # define what will be shown when someone calls "help $<your command>"
        self.help = "$clubstats | A CLI for the clubstats data server. Please see $clubstats --help for more information "
        
        self.author = "acp"
        self.last_updated = "August 22, 2022"

        self.is_nosy = True
        self.last_sniffed = '...'
        


    # define what the command does here.
    # this function must return a string. the string will be sent to the room.
    def run(self, event_pack: EventPackage):
        print(event_pack)
        endpoint = clubstats_endpoint + '/command'
        command_data = " ".join(event_pack.body)
        command_data = command_data.split(' ', 1)[1]
        data = {"command": command_data}
        print(data)
        r = requests.post(endpoint, json=data)
        content = r.content
        print(content)
        print(r.status_code)
        return f"{content.decode()}"


    def sniff_message(self, event_pack: EventPackage):
        self.last_sniffed = event_pack.event
        endpoint = clubstats_endpoint + '/new'
        json_data = json.dumps(event_pack.event.source, indent=4)
        # event_type = typeof(event_pack.event)
        print(f"Clubstats endpoint {endpoint}")
        print(f"posting {json_data}")
        r = requests.post(endpoint, json=event_pack.event.source)
        print(f"Clubstats endpoint {endpoint}")
        print(f"posting {event_pack.event}")
        return r.status_code
