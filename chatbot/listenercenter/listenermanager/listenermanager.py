from threading import Thread
from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler
import json

# important! this is where all the listener subclasses are discovered.
from ..listener import Listener
from ..listeners import *

g_body = ''
g_listener = Listener()
g_header_dict = dict()
g_identity_dict = dict()

class ListenerManager:
    def __init__(self, rooms, port):
        print("Starting listener manager...")
        self.rooms = rooms # dict of matrix room objects: { room_address : room_object }
        self.port = port # port the server will listen on
        self.server = HTTPServer(('', self.port), ListenerHandler) # minimal http server

        # build global identity dict
        global g_identity_dict

        for l in Listener.__subclasses__():
            listener = l()
            g_identity_dict[listener.identity] = listener

        print("The listener manager knows about these identities")
        for identity, listener in g_identity_dict.items():
            print(f"{identity} -> {listener.get_name()}")

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
        self.send_response(200)
        self.end_headers()
        print("I heard a GET!")

    def do_POST(self):
        global g_listener
        global g_body

        print("I heard a POST!")

        # save request body, if present
        if "Content-Length" in self.headers:
            g_body = self.rfile.read(int(self.headers["Content-Length"]))
        else:
            g_body = ''

        print("Checking for known identity...")
        for identity, listener in g_identity_dict.items():
            found = self.check_identity(identity, g_body)
            if found:
                print(listener.process(json.loads(g_body)))

        self.send_response(200)
        self.end_headers()

    def check_identity(self, id, body):
        # try-except block so evil body strings don't kill the bot

        try:
            dictionary = json.loads(body)
            
            id = id.replace(" ", '')
            print(f"id: {id}")

            value = str(id.split('=')[1])
            print(f"Desired value: {value}")
            
            position = 0

            while position != -1:
                openb = id.find('[', position)
                closeb = id.find(']', openb)
                position = id.find('[', closeb)

                key = id[openb + 1 : closeb]

                print(key)

                if key in dictionary:
                    dictionary = dictionary[key]
            
            if str(dictionary) == str(value):
                print("Match!")
                return True
            else:
                print("Mismatch!")
                return False
        except:
            print("There was an error in the identity matching function. Returning False.")
            return False
