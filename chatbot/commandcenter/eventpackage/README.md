# `eventpackage`

`eventpackage` contains the `EventPackage` class. This is a simple data sturcture to store information about room events together for easy function passing.

See the official matrix documentation for more information.

## Attributes

`self.body` : The body of the riot message. This is formatted as a list of the words in the body. For example, `self.body[0]` will be the first word (The command string, e.g. "$info") of the message body.

`self.room_id` : The room id corresponding the room that the riot event occured in.

`self.sender` : The sender of the message that invoked the riot event.

`self.event` : The rest of the riot event info.

## Methods

### `__init__(self, body={}, room_id="", sender="", event={})`
The constructor that gets called in `chat.py` whenever and event is recieved.

## Usage:

Every command gets passed an `EventPackage` (see `../commands/README.md`). The command is free to do what it pleases with this information.

Example usage inside of a command:

```python
# $echo

def run(self, event_pack: EventPackage):
    # event_pack.body is a list containing the words of the message.
    # this checks if there was at least two words in the message.
    if(len(event_pack.body) >= 2):
        output = " ".join(event_pack.body[i] for i in range(1, len(event_pack.body)))
        return output
    else:
        return "Needs more arguments, for example - \"$echo test\""
```
