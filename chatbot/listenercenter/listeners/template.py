# this file serves as a quick reference for the structure of a custom listener class.

# Template Listener
# By spacedog
# For educational purposes

from ..listener import Listener

class Template(Listener):
    def __init__(self):
        super().__init__() # important!
        self.name = "l_template" # name of the listener.

        # list of rooms that this listener is allowed to post in
        self.rooms = [
            '#bottest:cclub.cs.wmich.edu'
        ]

        # the "identity string"
        # this string tells the listener manager what kinds of request bodies activate this listener.
        #
        # imagine how you would access data in a dictionary.
        # in python, it would look like this:
        # dict["key"] = value
        #
        # or, in a multi-level dictionary:
        # dict["level1key"]["level2key"] = value
        # 
        # the identity string is meant to be similar to this syntax.
        #
        # for example, with this identity string:
        # self.identity = '[type] = template'
        # the listener manager will activate this listener when this request body is recieved:
        # {
        #   "type": "template"
        # }
        #
        # or this body:
        # {
        #   "type": "template",
        #   "foo" : "bar"
        # }
        #
        # but not this body:
        # {
        #   "foo" : {
        #     "type": "template"
        #   }
        # }
        #
        # you can do multi-level identity strings like this:
        # self.identity = '[multi][level][identity] = cool'
        # which would match something like this:
        # {
        #   "multi" : {
        #     "level" : {
        #       "identity" : cool
        #     }
        #   }
        # }
        #
        # it is best to keep the identity string as simple as possible 
        # while still being able to uniquely identify a request body.
        self.identity = '[type] = template'

    def process(self, body):
        # this is what happens when the listener is activated.
        # the body argument is the body of the request that was detected.
        # return a string, which will be sent to the chat rooms listed in __init__
        return "Beep boop, message from the template listener."
