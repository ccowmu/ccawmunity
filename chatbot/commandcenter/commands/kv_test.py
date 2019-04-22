from ..command import Command
from ..eventpackage import EventPackage

class KVTestCommand(Command):
    def __init__(self):
        self.name = "$kv"
        self.help = "$kv | do key-value stuff | Usage: $db get/set key [value]"
        self.author = "sphinx"
        self.last_updated = "April 22, 2019"

    def run(self, event_pack: EventPackage):
        length = len(event_pack.body)
        if(len(event_pack.body) < 3):
            return "Usage: $db get/set key [value]"
        else:
            command = event_pack.body[1]
            key = event_pack.body[2]

            if (command == "get"):
                value = self.kv_get(key)
                if None == value:
                    return "Key " + key + " not found!"
                else:
                    return value
            elif (command == "set"):
                if (length < 4):
                    return "Usage: $db get/set key [value]"

                value = event_pack.body[3]
                return str(self.kv_set(key, value))
            else:
                return "Usage: $db get/set key [value]"
