# Test Listener
# by spacedog
# Simply used to test if listener functionality is working
# To test: curl -d '{"type":"test"}' {ip}:{port}

from ..listener import Listener

class TestListener(Listener):
    def __init__(self):
        super().__init__()
        self.name = "l_test"
        self.rooms = [
            '#bottest:cclub.cs.wmich.edu'
        ]
        self.identity = '[type] = test'

    def process(self, body):
        return 'Test result: the listener system appears to be working!'
