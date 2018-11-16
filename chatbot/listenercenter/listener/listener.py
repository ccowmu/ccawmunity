class Listener:
    def __init__(self):
        self.name = "l_default"
        self.rooms = []
        self.identity = ""
    
    def process(self, body):
        print("Process")

    def __str__(self):
        return str(self.name)

    def get_name(self):
        return str(self.name)

    def get_rooms(self):
        return self.rooms

    def get_headers(self):
        return self.headers