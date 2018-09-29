# `commands`

`commands` contains all custom command classes. You should never have to instantiate or import anything from this module outside of `commandcenter`. It is used by `commander` to automatically load commands.

## How to create a new command

To create a new command:
1. Clone this repository.
2. Create a new branch for your command with `git checkout -b <name of your new branch>`
3. Create a python file called `<your new command>.py` in the `commands` directory.
4. Inside the new python file, create a custom command class that inherits from the `Command` parent class in the `command` module. See [the template file](./commands/template.py) if you want to see an example. 
5. When you're done, submit a pull request to this repo. Be sure to include what your command does within the pull request information.

## Attributes

`self.name` : The name of the command. This should be written exactly as you would write the command in chat when you call it. Be sure to include a dollar sign.

`self.help` : The command's help string as shown when the `$help` command is quried. It should follow this format:  
`$<command name> | <command purpose> | <usage instructions>`  
Example:  
`$info | Display info about a command. | Usage: $info <command (including the dollar sign)>`

`self.author` : The author of the command as shown when the `$info` command is queried.

`self.last_updated` : The date that the command was last updated as shown when the `$info` command is queried.

## Methods

### `__init__()`
Simple constructor in which you should set the above attributes.

### `run(event_pack: EventPackage)`
This is where you define what your custom command does. This method must return a string, which is what gets sent to the room. `event_pack` contains information about the event that triggered this command. See `../eventpackage`.

## Usage:

To create a new command, all that needs to be done is the creation of a class that follows this structure. The `commander` module will handle the rest and automatically load your command.

See `template.py` for an example.
