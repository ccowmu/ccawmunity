from ..listener import Listener

class GithubListener(Listener):
    def __init__(self):
        self.name = "l_github"
        self.rooms = ['#bottest:cclub.cs.wmich.edu']
        self.headers = [
            'X-Github-Event',
            'X-Github-Delivery',
            'X-Hub-Signature'
        ]

    def process(self, body):
        return body
