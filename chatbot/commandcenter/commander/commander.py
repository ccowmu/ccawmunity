import sys
import importlib

from os import listdir
from os.path import isfile, join, abspath, dirname

# important! this is where we discover all of the commands in the command directory.
# if this isn't called, Command.__subclasses__() is empty.
from ..commands import *
from .builtin import *

from ..command import Command
from ..eventpackage import EventPackage

class Commander:
    def __init__(self, prefix = "$"):
        self.commands = {}
        self.prefix = prefix

        print("Prefix: " + self.prefix)

        for command_class in Command.__subclasses__():
            command = command_class()
            self.commands[command.get_name()] = command

        print("Commander loaded with commands:")
        print(self.get_help_all())

    def run_command(self, command_string, event_pack: EventPackage):
        # convert command string to use $ as prefix in order to work with the internal syntax
        command_string_normalized = command_string.replace(self.prefix, "$")

        print("Commander: running command: {0}".format(command_string_normalized))

        if command_string_normalized == "$commands":
            print("Built in command: $commands")
            return self.get_help_all()

        if command_string_normalized == "$help":
            print("Built in command: $help")
            if len(event_pack.body) >= 2:
                return self.get_help(event_pack.body[1].replace(self.prefix, "$"))
            else:
                return self.get_help_all()

        if command_string_normalized == "$info":
            print("Built in command: $info")
            if len(event_pack.body) >= 2:
                return self.get_info(event_pack.body[1].replace(self.prefix, "$"))
            else:
                return "You must specify a command!"

        if command_string_normalized in self.commands:
            try:
                command = self.commands[command_string_normalized]
                return command.run(event_pack)
            except Exception as e:
                return "{} failed. Reason: {}".format(command_string_normalized, e)
        else:
            return self.command_not_recognized()
            
    def get_help(self, command_string):
        if command_string in self.commands:
            return self.commands[command_string].get_help().replace("$", self.prefix)
        else:
            return self.command_not_recognized()

    def get_info(self, command_string):
        if command_string in self.commands:
            command = self.commands[command_string]
            output = "Info for " + command_string.replace("$", self.prefix) + "...\n"
            output += "Last updated: " + command.get_last_updated() + "\n"
            output += "Author: " + command.get_author() + "\n"
            return output
        else:
            return self.command_not_recognized()

    def get_help_all(self):
        command_list = ""
        for label in self.commands:
            command_list += self.get_help(label) + "\n"
        return command_list

    def command_not_recognized(self):
        return "Command not recognized, please try \"$help\" for available commands".replace("$", self.prefix)
