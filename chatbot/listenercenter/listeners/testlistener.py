from ..listener import Listener

class TestListener(Listener):
    def __init__(self):
        self.name = "l_test"
        self.rooms = [
            '#bottest:cclub.cs.wmich.edu',
            '#ccawmunity:cclub.cs.wmich.edu'
            ]
        self.headers = [
            'X-Listener-Test'
        ]

    def process(self, body):
        return 'Test listener.'
