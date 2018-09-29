# `command`

`command` contains the `Command` class. This is the parent class for all custom functions.

## Attributes

`self.name` : The name of the command. This should be written exactly as you would write the command in chat when you call it. Be sure to include a dollar sign.

`self.help` : The command's help string as shown when the `$help` command is queried. It should follow this format:  
`$<command name> | <command purpose> | <usage instructions>`  
Example:  
`$info | Display info about a command. | Usage: $info <command (including the dollar sign)>`


`self.author` : The author of the command as shown when the `$info` command is queried.

`self.last_updated` : The date that the command was last updated as shown when the `$info` command is queried.

## Methods

### `__init__()`
Simple constructor which sets the above mentioned attributes to their default values.

### `__str__()`
Returns `self.name` for easy printing.

### `get_name()`
Returns `str(self.name)`

### `get_help()`
Returns `str(self.help)`

### `get_author()`
Returns `str(self.author)`

### `get_last_updated()`
Returns `str(self.last_updated)`

## Usage:

You should never directly instantiate this class. This class is used as a base class for custom commands. See `../commands/README.md`.
