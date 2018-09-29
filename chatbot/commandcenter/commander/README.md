# `commander`

`commander` contains the `Commander` class. Another good name for this class would be "command manager". Its job is to run commands and load commands.

## Attributes

`self.commands` : A dictionary that maps a command string (The command name, e.g. "$info") to a command object. It gets populated automatically in `Commander`'s constructor.

## Methods

### `__init__()`
The constructor. This is where the commands in the commands directory are automatically loaded.

### `run_command(command_string, event_pack: EventPackage)`
Attempts to find a command that the commander knows with the name matching `command_string`. If it finds one, it will run the command and pass it `event_pack`.

`$info` and `$help` are defined in this class. They are "meta" commands and built into the commander, rather than being built as commands in the command directory.

### `get_help(command_string)`
Returns a printable string containing help information about the passed command, if the command exists.

### `get_info(command_string)`
Returns a printable string containing general information about the passed commmand, if it exists.

### `get_help_string(command_string = '')`
If `command_string` is the name of a command (including the dollar sign), this function returns a printable string containing help information about the command. (By calling `get_help`)

Otherwise, it returns a printable string containing the summary of all loaded commands. This function is what gets called when the `$help` command is invoked.

### `command_not_recognized()`
Defines what happens when a command cannot be found in the command dictionary.

## Usage:

Import the class and instantiate it:

```python
from commandcenter.commander import Commander
c = Commander()
```

At this time, the commands directory will be searched for commands.

Then, to run a command:

```python
room.send_text(c.run_command("$info", event_pack)) 
# event_pack definied elsewhere
```
