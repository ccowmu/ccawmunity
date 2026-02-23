#!/usr/bin/env python3

import asyncio
import getpass
import re
import shlex
from os import environ

from nio import (AsyncClient, MatrixRoom, RoomMemberEvent, RoomMessageImage,
                 RoomMessageText, RoomMessageVideo)

import botconfig
import timekeeping as tk
from commandcenter import command
from commandcenter.commander import Commander
from commandcenter.eventpackage import EventPackage

g_commander = Commander(botconfig.command_prefix, botconfig.command_timeout)

def get_password():
    # try to find password in the BOT_PASSWORD environment variable
    if "BOT_PASSWORD" in environ and environ["BOT_PASSWORD"] != "":
        print("Obtained password from BOT_PASSWORD environment variable.")
        return environ["BOT_PASSWORD"]
    else:
        print("No BOT_PASSWORD environment variable has been set.")
    return getpass.getpass(prompt='Password required for {}: '.format(botconfig.username))

async def room_send_text(room_id, text):
    global g_client

    if g_client is None:
        print("ERROR | Tried to send room text with a null client")
        return

    return await g_client.room_send(
        room_id = room_id,
        message_type="m.room.message",
        content = {
            "msgtype": "m.text",
            "body": str(text)
        }
    )

async def room_send_code(room_id, text):
    global g_client

    if g_client is None:
        print("ERROR | Tried to send room text with a null client")
        return

    return await g_client.room_send(
        room_id = room_id,
        message_type="m.room.message",
        content = {
            "msgtype": "m.text",
            "body": str(text),
            "format": "org.matrix.custom.html",
            "formatted_body": "<pre><code>" + str(text) + "</code></pre>"
        }
    )

async def room_send_big(room_id, text):
    global g_client

    if g_client is None:
        print("ERROR | Tried to send room text with a null client")
        return

    return await g_client.room_send(
        room_id = room_id,
        message_type="m.room.message",
        content = {
            "msgtype": "m.text",
            "body": str(text),
            "format": "org.matrix.custom.html",
            "formatted_body": "<h1>" + str(text) + "</h1>"
        }
    )

async def room_send_rainbow(room_id, text):
    global g_client

    if g_client is None:
        print("ERROR | Tried to send room text with a null client")
        return

    return await g_client.room_send(
        room_id = room_id,
        message_type="m.room.message",
        content = {
            "msgtype": "m.text",
            "body": str(text),
            "format": "org.matrix.custom.html",
            "formatted_body": str(text)
        }
    )

def time_filter(event):
    # on startup, the bot will receive every historical event ever...
    # make sure we don't run commands from the past!
    # we wait to process anything until we see this session's unique uuid
    if not tk.time_has_started() and hasattr(event, "body") and event.body == tk.get_session_startup_string():
        tk.start_time(event.server_timestamp)
        return False

    if not tk.time_has_started():
        return False

    # Only process events that happened after the beginning of time
    return event.server_timestamp >= tk.get_beginning_of_time()


# safely convert input string into a list
def safe_split(text):
    # Matches last " char in string
    pattern = re.compile(r'\"(?!.*\")')
    # If there's a quote that isn't closed, replace the last " char with '
    text = pattern.sub("'", text) if text.count('"') % 2 != 0 else text

    # split string on whitespace, preserving anything in double quotes
    s = shlex.shlex(text, posix=True)
    s.quotes = '"'
    s.whitespace_split = True
    s.commenters = ''
    return list(s)

# -- callbacks -----------------------------------------------------------------

# take a CommandResponse and do the appropriate action (send text, send state, ...)
async def handle_command_result(room: MatrixRoom, response: command.CommandResponse):
    global g_client

    # code response is a subclass of text response, so be sure to always check
    # for it first.
    if isinstance(response, command.CommandCodeResponse):
        log_response = response.text.replace("\n", "\\n")
        print(f"-> {log_response}")

        return await room_send_code(room.room_id, response)

    if isinstance(response, command.CommandRainbowResponse):
        log_response = response.text.replace("\n", "\\n")
        print(f"-> {log_response}")

        if room.room_id == botconfig.ROOM_ID_GEEKS:
            if len(response) <= botconfig.spam_limit:
                return await room_send_rainbow(room.room_id, response)
            else:
                return await room_send_text(room.room_id, "Too spammy! >:(")
        else:
            return await room_send_rainbow(room.room_id, response)

    if isinstance(response, command.CommandBigResponse):
        log_response = response.text.replace("\n", "\\n")
        print(f"-> {log_response}")

        return await room_send_big(room.room_id, response)

    if isinstance(response, command.CommandTextResponse):
        log_response = response.text.replace("\n", "\\n")
        print(f"-> {log_response}")

        # send response, but don't spam #geeks
        if room.room_id == botconfig.ROOM_ID_GEEKS:
            if len(response) <= botconfig.spam_limit:
                return await room_send_text(room.room_id, response)
            else:
                return await room_send_text(room.room_id, "Too spammy! >:(")
        else:
            return await room_send_text(room.room_id, response)

    if isinstance(response, command.CommandStateResponse):
        print(f"-> {response}")
        return await g_client.room_put_state(
            room_id = room.room_id,
            event_type = response.type,
            content = response.content
        )

# called when a text message is sent in a room
async def on_message(room: MatrixRoom, event: RoomMessageText):
    global g_commander
    global g_client

    if not time_filter(event):
        return

    print(f"{room.user_name(event.sender)[:16]}: {event.body}")

    # ignore senders in ignore list
    if event.sender in botconfig.ignored:
        print("INFO | (ignored)")
        return

    # construct data for command machinery
    argv = safe_split(event.body)
    command_string = argv[0]
    event_package = EventPackage(
        body=argv, room_id=room.room_id, sender=event.sender, event=event)

    # just for fun... send a typing notification
    if g_commander.is_command(command_string):
        await g_client.room_typing(
            room.room_id, True, timeout=(botconfig.command_timeout * 1000)
        )

    # silently ignore commands handled by other bots
    if command_string in botconfig.ignored_commands:
        return

    # run command
    result = g_commander.run_command(command_string, event_package)

    # done typing
    if g_commander.is_command(command_string):
        await g_client.room_typing(room.room_id, False)

    # handle command result
    if result is not None:
        # backwards compatibility: most commands will return raw strings
        if isinstance(result, str):
            result = command.CommandTextResponse(result)

        await handle_command_result(room, result)

# delete 'event' from the passed room
async def redact_media(room: MatrixRoom, event):
    await room_send_text(room.room_id, f"{event.sender} please post images in #img:cclub.cs.wmich.edu and link them here.")
    await g_client.room_redact(room.room_id, event.event_id, reason="Please post images in #img and linke them here")

# called when an image is sent in a room
async def on_image(room: MatrixRoom, event: RoomMessageImage):
    if not time_filter(event):
        return

    if room.room_id == botconfig.ROOM_ID_GEEKS:
        print(f"INFO | removing image in {room.machine_name}")
        await redact_media(room, event)

# called when a video is sent in a room
async def on_video(room: MatrixRoom, event: RoomMessageVideo):
    if not time_filter(event):
        return

    if room.room_id == botconfig.ROOM_ID_GEEKS:
        print(f"INFO | removing video in {room.machine_name}")
        await redact_media(room, event)

# create a DM with the person in 'event' and send a welcome message
async def send_geeks_welcome_message(room: MatrixRoom, event: RoomMemberEvent):
    global g_client

    member = event.sender

    # create a private room and invite
    new_room = await g_client.room_create(name="Welcome to CClub!", is_direct=True, invite=[member])

    # gets username without :cclub.cs.wmich.edu
    member_name = member.split(":")[0][1:]

    # send info
    with open("./static/welcome-message.txt", "r") as f:
        return await room_send_text(new_room.room_id, f.read().format(member_name))

def should_pm_welcome(room: MatrixRoom, event: RoomMemberEvent):
    return event.membership == "join" \
        and room.room_id == botconfig.ROOM_ID_GEEKS \
        and event.prev_content is None

# called when someone's membership in a room changes
async def on_membership(room: MatrixRoom, event: RoomMemberEvent):
    if not time_filter(event):
        return

    # PM newbies
    if should_pm_welcome(room, event) is True:
        return await send_geeks_welcome_message(room, event)

    return

async def main():
    global g_client

    print("Connecting to server: {}".format(botconfig.client_url))
    g_client = AsyncClient(botconfig.client_url, f"@{botconfig.username}:cclub.cs.wmich.edu")

    # log in
    password = get_password()
    print(await g_client.login(password))

    # figure out what time it is
    await room_send_text(botconfig.ROOM_ID_BOTTOY, tk.get_session_startup_string())

    # register event callbacks
    g_client.add_event_callback(on_message, RoomMessageText)
    g_client.add_event_callback(on_image, RoomMessageImage)
    g_client.add_event_callback(on_video, RoomMessageVideo)
    g_client.add_event_callback(on_membership, RoomMemberEvent)

    # loop forever
    await g_client.sync_forever(timeout=120000) # two minutes

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
