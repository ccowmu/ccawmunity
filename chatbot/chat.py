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
import getpass
from os import environ

import botconfig

from matrix_client.client import MatrixClient
from matrix_client.api import MatrixRequestError
from requests.exceptions import MissingSchema

from functools import partial

from commandcenter.commander import Commander
from commandcenter.eventpackage import EventPackage

from listenercenter.listenermanager import ListenerManager

g_commander = Commander(botconfig.command_prefix, botconfig.command_timeout)

def get_password():
    # try to find password in the BOT_PASSWORD environment variable
    if "BOT_PASSWORD" in environ and environ["BOT_PASSWORD"] is not "":
        print("Obtained password from BOT_PASSWORD environment variable.")
        return environ["BOT_PASSWORD"]
    else:
        print("No BOT_PASSWORD environment variable has been set.")
    return getpass.getpass(prompt='Password required for {}: '.format(botconfig.username))

# triggered when someone joins geeks.
# member comes from event["sender"]
def send_geeks_welcome_message(member):
    global g_client

    # create a private room and invite
    room = g_client.create_room(invitees=[member])
    room.add_listener(on_message)
    print("Joined room: {}".format(room))

    member_name = member.split(":")[0][1:] # gets username without :cclub.cs.wmich.edu

    # send info
    with open("./static/welcome-message.txt", "r") as f:
        room.send_text(f.read().format(member_name))

# called when a message is recieved.
def on_message(room, event):
    global g_commander
    
    if event['type'] == "m.room.member":
        if event['membership'] == "join":
            print("{0} joined".format(event['content']['displayname']))

            # if event['room_id'] == botconfig.ROOM_ID_GEEKS:
            #     send_geeks_welcome_message(event["sender"])

    elif event['type'] == "m.room.message":
        if event['content']['msgtype'] == "m.text":
            print("{0}: {1}".format(event['sender'], event['content']['body']))

            # ignore anyone in the ignore list
            if(event['sender'] in botconfig.ignored):
                return

            # create responses for messages starting with the command prefix
            # compares the first x characters of a message to the command prefix,
            # where x = len(command.prefix)
            if(event['content']['body'][0:len(botconfig.command_prefix)] == botconfig.command_prefix):
                output = event['content']['body'].split(" ")
                command_string = output[0]

                print("Command detected: {0}".format(command_string))
                event_package = EventPackage(body=output, room_id=event["room_id"], sender=event["sender"], event=event)

                room.send_text(g_commander.run_command(command_string, event_package))
    else:
        print(event['type'])

    try:
        # check if room is geeks and redact
        if event['room_id'] == botconfig.ROOM_ID_GEEKS and (event['content']['msgtype'] == "m.image" or event['content']['msgtype'] == "m.video"):
            room.send_text(event['sender'] + " please post images in #img:cclub.cs.wmich.edu and link them here")
            room.redact_message(event['event_id'], reason="Please post images in #img and link them here")
    except KeyError:
        # expecting matrix lib sync to be checking the key when it no longer exists
        pass

# called when an invite is received.
def on_invite(room_id, state):
    global g_client

    # dump info
    print("Invite received: {}".format(room_id))
    print("Invite state:")
    print(state)

    # join room
    room = g_client.join_room(room_id)
    room.add_listener(on_message)
    print("Joined room: {}".format(room))

    # notice
    room.send_text("(Note: after a bot restart, you will have to re-invite the bot to this room.)")

def main():
    global g_client
    print("Connecting to server: {}".format(botconfig.client_url))
    g_client = MatrixClient(botconfig.client_url)

    password = get_password()

    try:
        print("Logging in with username: {}".format(botconfig.username))
        g_client.login_with_password(botconfig.username, password)
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

    # room dictionary that will be passed to the listener manager
    rooms = {}

    for room_address in botconfig.rooms:
        try:
            room = g_client.join_room(room_address)
            room.add_listener(on_message)
            rooms[room_address] = room
            print("Joined room: {}".format(room_address))
        except MatrixRequestError as e:
            print(e)
            if e.code == 400:
                print("{}: Room ID/Alias in the wrong format".format(room_address))
                sys.exit(11)
            else:
                print("Couldn't find room: {}".format(room_address))
                sys.exit(12)

    g_client.add_invite_listener(on_invite)

    g_client.start_listener_thread()

    listener = ListenerManager(rooms, botconfig.listener_port)

    listener.start_listener_thread()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Shutting down.")

if __name__ == '__main__':
    logging.basicConfig(level=logging.WARNING)
    main()
