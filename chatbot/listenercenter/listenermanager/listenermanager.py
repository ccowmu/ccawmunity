from threading import Thread
from http.server import HTTPServer

from ..listenerserver import ListenerHandler

class ListenerManager:
    def __init__(self, rooms):
        print("Starting listener manager...")
        self.rooms = rooms # dict of matrix room objects: { room_address : room_object }
        self.server = HTTPServer(('', 7890), ListenerHandler) # minimal http server
        self.thread = Thread(target=self.listen_forever) # thread that the server is running on

        print("Listener manager knows about these rooms:")
        for room_address in rooms:
            print(room_address)

    def start_listener_thread(self):
        self.thread.start()

    def listen_forever(self):
        self.server.serve_forever()