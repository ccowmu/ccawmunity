#!/usr/bin/env python3

# A simple chat client for matrix.
# This sample will allow you to connect to a room, and send/recieve messages.
# Args: host:port username password room
# Error Codes:
# 1 - Unknown problem has occured
# 2 - Could not find the server.
# 3 - Bad URL Format.
# 4 - Bad username/password.
# 11 - Wrong room format.
# 12 - Couldn't find room.

import sys
import logging

from matrix_client.client import MatrixClient
from matrix_client.api import MatrixRequestError
from requests.exceptions import MissingSchema

from functools import partial
from commands import *

# called when a message is recieved.
def on_message(room, event):
    if event['type'] == "m.room.member":
        if event['membership'] == "join":
            print("{0} joined".format(event['content']['displayname']))
    elif event['type'] == "m.room.message":
        if event['content']['msgtype'] == "m.text":
            print("{0}: {1}".format(event['sender'], event['content']['body']))

            # ignore anything the bot might send to itself
            if(event['sender'] == "@ccawmu:cclub.cs.wmich.edu"):
                return

            # create responses for messages starting with $
            if(event['content']['body'][0] == '$'):

                output = event['content']['body'].split(" ")
                command = output[0]

                # if the command is in our dictionary of functions, use it (from commands.py)
                if command in COMMANDLIST:
                    room.send_text(COMMANDLIST[command](body=output, roomId=event["room_id"], sender=event["sender"], event=event))
                else:
                    room.send_text("Command not recognized, please try \"$commands\" for available commands")
    else:
        print(event['type'])


def main(password):
    client = MatrixClient("https://cclub.cs.wmich.edu")

    try:
        client.login_with_password("ccawmu", password)
    except MatrixRequestError as e:
        print(e)
        if e.code == 403:
            print("Bad username or password.")
            sys.exit(4)
        else:
            print("Check your sever details are correct.")
            sys.exit(2)
    except MissingSchema as e:
        print("Bad URL format.")
        print(e)
        sys.exit(3)

    try:
        room = client.join_room("#ccawmunity:cclub.cs.wmich.edu")
    except MatrixRequestError as e:
        print(e)
        if e.code == 400:
            print("Room ID/Alias in the wrong format")
            sys.exit(11)
        else:
            print("Couldn't find room.")
            sys.exit(12)

    room.add_listener(on_message)
    client.start_listener_thread()

    while True:
        msg = input()

if __name__ == '__main__':

    logging.basicConfig(level=logging.WARNING)
    
    #grab pass as argv for now 
    password = sys.argv[1] 
     
    main(password)
