from http.server import BaseHTTPRequestHandler

class ListenerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        print("I heard a GET!")

    def do_POST(self):
        print("I heard a POST!")