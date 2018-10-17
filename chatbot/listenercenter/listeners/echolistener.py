from ..listener import Listener

class EchoListener(Listener):
    def __init__(self):
        self.name = "l_echo"
        self.rooms = [
            '#bottest:cclub.cs.wmich.edu',
            '#ccawmunity:cclub.cs.wmich.edu'
            ]
        self.headers = [
            'X-Listener-Echo'
        ]
        self.identity = '[test] = 1'

    def process(self, body):
        return body.decode('utf-8')
