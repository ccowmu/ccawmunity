# this file serves as a quick reference for the structure of a custom listener class.

# Github Listener
# By spacedog
# tests listening to an actual webhook

from ..listener import Listener

class TestGithubListener(Listener):
    def __init__(self):
        super().__init__() # important!
        self.name = "l_test_github" # name of the listener.

        # list of rooms that this listener is allowed to post in
        self.rooms = [
            '#bottest:cclub.cs.wmich.edu'
            ]

        self.identity = '[repository][full_name] = verdog/listenertest'

    def process(self, body):
        # this is what happens when the listener is activated.
        # the body argument is the body of the request that was detected.
        # return a string, which will be sent to the chat rooms listed in __init__
        
        return "New issue in super secret repository " + body["repository"]["full_name"]
