from ..command import Command
from ..eventpackage import EventPackage

import random

class GetQuoteCommand(Command):
    def __init__(self):
        self.name = "$getquote" # this is required in order for the command to run!
        self.help = "$getquote | usage: random quote: $getquote, quote number: $getquote <number>, quote from user: $getquote username"
        self.author = "spacedog"
        self.last_updated = "August 27, 2018"

    def run(self, event_pack: EventPackage):
        self.raw_db = True

        if len(event_pack.body) == 1:
            # just $getquote
            quotelist = self.db_list_get("command:addquote:all_quotes")
            idx = random.randrange(len(quotelist))
            r = "(" + str(idx + 1) + "): " + quotelist[idx].decode("utf-8") # comes back as bytes
        else:
            parameter = event_pack.body[1]
            # check if it's an integer
            try:
                number = int(parameter) - 1

                quotelist = self.db_list_get("command:addquote:all_quotes")
                if number < len(quotelist) and number >= 0:
                    r = quotelist[number].decode("utf-8")
                else:
                    r = "Invalid index!"
            except:
                # not an int, must be a user
                user = parameter
                quotelist = self.db_set_get("command:addquote:" + user)

                if len(quotelist) > 0:
                    r = random.sample(quotelist, 1)[0].decode("utf-8")
                else:
                    r = "No quotes for that user!"

        return r
