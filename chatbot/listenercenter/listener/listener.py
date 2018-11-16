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
