from ..eventpackage import EventPackage

class Command:
    def __init__(self):
        self.name = "$default_command_object"
        self.help = "...looks like self.help never got defined for " + self.name + "..."
        self.author = "...who knows? (They forgot to set the author value!)"
        self.last_updated = "20XX (No date found)"

    def __str__(self):
        return self.name

    def run(self, eventpackage: EventPackage):
        return "This command doesn't have an implementation yet!"

    def get_name(self):
        return str(self.name)

    def get_help(self):
        return str(self.help)

    def get_author(self):
        return str(self.author)

    def get_last_updated(self):
        return str(self.last_updated)
