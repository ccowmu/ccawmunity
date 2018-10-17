from threading import Thread
from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler

# important! this is where all the listener subclasses are discovered.
from ..listeners import *

from ..listener import Listener

g_body = ''
g_listener = Listener()
g_header_dict = dict()

class ListenerManager:
    def __init__(self, rooms, port):
        print("Starting listener manager...")
        self.rooms = rooms # dict of matrix room objects: { room_address : room_object }
        self.port = port # port the server will listen on
        self.server = HTTPServer(('', self.port), ListenerHandler) # minimal http server

        # build global header dict
        global g_header_dict

        for l in Listener.__subclasses__():
            listener = l()
            for header in listener.headers:
                g_header_dict[header] = listener

        print("The listener manager knows about these headers:")
        for header, listener in g_header_dict.items():
            print(f"{header} -> {listener.get_name()}")

        print("The listener manager knows about these rooms:")
        for room_address in rooms:
            print(room_address)

    def start_listener_thread(self):
        print(f"Started listening on port {self.port}")
        Thread(target=self._listen_forever, daemon=True).start()

    def _listen_forever(self):
        while True:
            self.server.handle_request()
            self._process_results()

    def _process_results(self):
        global g_listener
        
        if g_listener is not None:
            body = g_body
            listener = g_listener

            # for every room that the listener has registered, send the response.
            for room_address in [r for r in self.rooms if r in listener.get_rooms()]:
                print(f"Sending response to {room_address}...")
                # self.rooms[room_address].send_text(listener.process(body))
                print(listener.process(body))

        else:
            print("No listener detected!")

class ListenerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        print("I heard a GET!")

    def do_POST(self):
        global g_listener
        global g_body

        print("I heard a POST!")

        print("Looking for headers in dict...")
        for header in self.headers:
            if header in g_header_dict:
                g_listener = g_header_dict[header]
                print(f"Detected {header}, selecting {g_listener.name}.")
                break

        g_body = self.rfile.read(32)