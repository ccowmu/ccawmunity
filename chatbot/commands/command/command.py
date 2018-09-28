class Command:
    def __init__(self):
        self.name = "$default_command_object"

    def __str__(self):
        return self.name

    def run(self, body={}, roomId="", sender="", event={}):
        return "This command doesn't have an implementation yet!"

    def get_help(self):
        return "$default - The default command abstract class. You probably shouldn't be seeing this text."
