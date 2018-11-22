# This is the parent class for listeners.
# If you are trying to make a custom listener, you shouldn't be editing this file.
# Instead, make a .py file in the listeners directory.

class Listener:
    def __init__(self):
        self.name = "l_default"
        self.rooms = []
        self.identity = ""
    
    def process(self, body):
        print("This is coming from the default process event in Listener superclass, which probably shouldn't have happened.")

    def __str__(self):
        return str(self.name)

    def get_name(self):
        return str(self.name)

    def get_rooms(self):
        return self.rooms
