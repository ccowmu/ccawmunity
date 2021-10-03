# with matrix-nio, on bot startup, a bunch of old events flood in.
# of course, we don't want to response to these old events, so we need
# a way to figure out which ones are old, and which are new.
#
# we do this by sending a message on bot startup and noting the server
# timestamp on the message event when we read it back. we only handle
# messages that are newer than that time.

import uuid

_SESSION_ID = None
_BEGINNING_OF_TIME = None

def time_has_started():
    return _BEGINNING_OF_TIME is not None

def start_time(time):
    global _BEGINNING_OF_TIME
    _BEGINNING_OF_TIME = time
    print(f"INFO | The beginning is officially {_BEGINNING_OF_TIME}")

def get_beginning_of_time():
    global _BEGINNING_OF_TIME
    if not time_has_started():
        return None
    return _BEGINNING_OF_TIME

def generate_session_uuid():
    global _SESSION_ID
    _SESSION_ID = uuid.uuid4().hex
    print(f"INFO | new session id: {_SESSION_ID}")

def get_session_startup_string():
    if not _SESSION_ID:
        generate_session_uuid()
    
    return f"Hello world! {_SESSION_ID}"
