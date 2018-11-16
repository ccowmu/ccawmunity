from ..listener import Listener

class TestListener2(Listener):
    def __init__(self):
        super().__init__()
        self.name = "l_test2"
        self.rooms = [
            '#bottest:cclub.cs.wmich.edu',
            # '#ccawmunity:cclub.cs.wmich.edu'
            ]
        self.identity = '[test][type] = 2'

    def process(self, body):
        return 'Test listener 2.'
