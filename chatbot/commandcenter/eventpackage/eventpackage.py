class EventPackage:
    def __init__(self, body={}, room_id="", sender="", event={}):
        self.body = body
        self.room_id = room_id
        self.sender = sender
        self.event = event