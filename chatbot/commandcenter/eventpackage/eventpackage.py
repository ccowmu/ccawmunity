class EventPackage:
    def __init__(self, body={}, roomId="", sender="", event={}):
        self.body = body
        self.roomId = roomId
        self.sender = sender
        self.event = event