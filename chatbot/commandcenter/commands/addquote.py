from ..command import Command
from ..eventpackage import EventPackage

class AddQuoteCommand(Command):
    def __init__(self):
        self.name = "$addquote" # this is required in order for the command to run!
        self.help = "$addquote | usage: $addquote <quote>"
        self.author = "spacedog"
        self.last_updated = "August 27, 2018"

    def run(self, event_pack: EventPackage):
        user = event_pack.body[1]
        quote = " ".join(event_pack.body[2:])

        # clean up user so we can easily find it again
        for c in "><:":
            user = user.replace(c, "")

        # how the quote will look when displayed
        full_string = user + ": " + quote

        # add quote to general list
        r1 = self.db_append("all_quotes", full_string)

        # add quote to user set
        r2 = self.db_set_add(user, full_string)

        if r1 != 0 and r2 != 0:
            number = self.db_list_len("all_quotes")
            return "Added quote {}!".format(number)
        else:
            if r1 != 0:
                self.db_pop("all_quotes")
            if r2 != 0:
                self.db_set_remove(user, full_string)
            else:
                return "That's already been added!"
            return "Something went wrong! ({} {})".format(r1, r2)
