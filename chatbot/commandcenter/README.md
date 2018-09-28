# `commandcenter`

the `commandcenter` package contains everything needed to use a `commander` object. It also contains the `commands` directory, which is where all the source code for all commands is stored.

This document with provide a general overview of all of the packages. There is be package specific documentation (where you can find more details) in each directory.

## `command`

The `command` package contains the `Command` class, which is the base class for all custom 
command classes.

To import (from outside of the `commandcenter` package):  
`from commandcenter.command import Command`

## `commander`

The `commander` package contains the `Commander` class. This class manages the execution of custom command classes. It automatically detects all custom command classes in the `./commands` directory. It also handles meta commands such as `$info` and `$help`.

To import (from outside of the `commandcenter` package):  
`from commandcenter.commander import Commander`

## `commands`

The `commands` package contains all custom classes that inherit from `Command` class. You should not need to import anything from this class anywhere outside of the `commandcenter` package.

## `eventpackage`

The `eventpackage` package contains the `EventPackage` class. This class is simply a data structure to hold information about room events.

# How to create a new command

To create a new command:
1. Clone this repository.
2. Create a new branch for your command with `git checkout -b <name of your new branch>`
3. Create a python file called `<your new command>.py` in the `commands` directory.
4. Inside the new python file, create a custom command class that inherits from the `Command` parent class in the `command` module. See [the template file](./commands/template.py) if you want to see an example. Check `./commands/README.md` for more details on what your command class should look like.
5. When you're done, submit a pull request into the this repo. Be sure to include what your command does within the pull request information.