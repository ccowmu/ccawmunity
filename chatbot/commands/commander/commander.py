from os import listdir
from os.path import isfile, join

from ..command import Command

import sys
import importlib

class Commander:
    def __init__(self):
        self.commands = []

    def run_command(self, command: Command):
        if command in self.commands:
            return command.run() # PLACEHOLDER - incorrect args here...
        else:
            return "Command not recognized, please try \"$commands\" for available commands"
            
    def get_help(self, command: Command):
        if command in self.commands:
            return command.getHelp()
        else:
            return "Command not recognized, please try \"$commands\" for available commands"

    def load_commands_from_directory(self, directory):
        print("Loading commands from " + str(directory) + "...")
        self.commands = [f for f in listdir(directory) if isfile(join(directory, f))]

        self.commands.remove("__init__.py")

        # import all detected classes
        for f in self.commands:
            try:
                importlib.import_module("commands." + f.split(".")[0])
            except ImportError:
                sys.stderr.write("ERROR: missing python module: " + f + "\n")

        # converts "xyz.py" to "$xyz"
        self.commands = ["$" + s.split(".")[0] for s in self.commands]

    def get_loaded_commands_pretty(self):
        commandList = ""
        for command in self.commands:
            commandList += command.getHelp() + "\n"
        return commandList

    def get_loaded_commands(self):
        return self.commands