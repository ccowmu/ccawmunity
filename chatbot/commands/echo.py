from .command import Command

class EchoCommand(Command):
    def __init__(self):
        self.name = "$echo"

    def run(self, body={}, roomId="", sender="", event={}):
        if(len(body) >= 2):
            output = " ".join(body[i] for i in range(1, len(body)))
            return output
        else:
            return "Needs more arguments, for example - \"$echo test\""

    def getHelp(self):
        return "$echo - N parameters accepted separated by spaces, bot echoes them back to chat.\"$echo arg1 arg2\""