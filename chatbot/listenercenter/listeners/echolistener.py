# Echo Listener
# By spacedog
# Simply returns the contents of body["message"]

from ..listener import Listener

class EchoListener(Listener):
    def __init__(self):
        super().__init__()
        self.name = "l_echo"
        self.rooms = [
            '#bottest:cclub.cs.wmich.edu'
            ]
        self.identity = '[type] = echo'

    def process(self, body):
        return body["message"]
