from threading import Thread
from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler

class Listener:
    def __init__(self):
        self.name = "l_default"
        self.rooms = []
        self.headers = []
    
    def process(self, body):
        print("Process")

    def __str__(self):
        return str(self.name)

g_body = ''
g_listener = Listener()
g_header_dict = dict()

class ListenerManager:
    def __init__(self, rooms):
        print("Starting listener manager...")
        self.rooms = rooms # dict of matrix room objects: { room_address : room_object }
        self.server = HTTPServer(('', 8978), ListenerHandler) # minimal http server
        self.thread = Thread(target=self.listen_forever) # thread that the server is running on

        print(self.server.server_address)

        # build global header dict
        global g_header_dict

        for l in Listener.__subclasses__():
            listener = l()
            for header in listener.headers:
                g_header_dict[header] = listener

        print("Listener manager knows about these headers:")
        for header in g_header_dict:
            print(header)

        print("Listener manager knows about these rooms:")
        for room_address in rooms:
            print(room_address)

    def start_listener_thread(self):
        self.thread.start()

    def listen_forever(self):
        while True:
            self.server.handle_request()
            self.process_request()

    def process_request(self):
        global g_listener
        
        if g_listener is not None:
            body = g_body
            listener = g_listener

            for room in [self.rooms[r] for r in self.rooms if r in listener.rooms]:
                room.send_text(listener.process(body))

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

class GithubListener(Listener):
    def __init__(self):
        self.name = "l_github"
        self.rooms = ['#bottest:cclub.cs.wmich.edu']
        self.headers = [
            'X-Github-Event',
            'X-Github-Delivery',
            'X-Hub-Signature'
        ]

    def process(self, body):
        return body

class EchoListener(Listener):
    def __init__(self):
        self.name = "l_echo"
        self.rooms = [
            # '#bottest:cclub.cs.wmich.edu',
            '#ccawmunity:cclub.cs.wmich.edu'
            ]
        self.headers = [
            'X-Listener-Echo'
        ]

    def process(self, body):
        return body.decode('utf-8')