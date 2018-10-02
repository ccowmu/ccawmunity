import sys
import importlib

from os import listdir
from os.path import isfile, join, abspath, dirname

# important! this is where we discover all of the commands in the command directory.
# if this isn't called, Command.__subclasses__() is empty.
from ..commands import *

from ..command import Command
from ..eventpackage import EventPackage

# dummy classes of the built-in commands so that they are compatible with commands like $help or $info

class HelpCommand(Command):
    def __init__(self):
        self.name = "$help" # this is required in order for the command to run!
        self.help = "$help - Learn about commands. Usage: `$help` or `$help <command (including the dollar sign)>`"
        self.author = "spacedog"
        self.last_updated = "Sept. 28, 2018"

    def run(self, event_pack: EventPackage):
        return "This command is built in to the commander. You should never see this text. Uh oh."

class InfoCommand(Command):
    def __init__(self):
        self.name = "$info" # this is required in order for the command to run!
        self.help = "$info - Display info about a command. Usage: `$info <command (including the dollar sign)>`"
        self.author = "spacedog"
        self.last_updated = "Sept. 28, 2018"

    def run(self, event_pack: EventPackage):
        return "This command is built in to the commander. You should never see this text. Uh oh."

class Commander:
    def __init__(self):
        self.commands = {}

        for command_class in Command.__subclasses__():
            command = command_class()
            self.commands[command.get_name()] = command
            print("Loaded command: " + command.get_name())

    def run_command(self, command_string, event_pack: EventPackage):
        print("Commander: running command: {0}".format(command_string))

        if command_string == "$commands":
            print("Built in command: $commands")
            return self.get_help_string()

        if command_string == "$help":
            print("Built in command: $help")
            if len(event_pack.body) >= 2:
                command_string = event_pack.body[1]
            else:
                command_string = ''
            return self.get_help_string(command_string)

        if command_string == "$info":
            print("Built in command: $info")
            if len(event_pack.body) >= 2:
                command_string = event_pack.body[1]
            else:
                return "You must specify a command!"
            return self.get_info(command_string)

        if command_string in self.commands:
            try:
                command = self.commands[command_string]
                return command.run(event_pack)
            except Exception as e:
                return "{} failed. Reason: {}".format(command_string, e)
        else:
            return self.command_not_recognized()
            
    def get_help(self, command_string):
        if command_string in self.commands:
            return self.commands[command_string].get_help()
        else:
            return self.command_not_recognized()

    def get_info(self, command_string):
        if command_string in self.commands:
            command = self.commands[command_string]
            output = "Info for `" + command_string + "`...\n"
            output += "Last updated: " + command.get_last_updated() + "\n"
            output += "Author: " + command.get_author() + "\n"
            return output
        else:
            return self.command_not_recognized()

    def get_help_string(self, command_string = ''):
        if command_string == '':
            command_list = ""
            for label in self.commands:
                command = self.commands[label]
                command_list += command.get_help() + '\n'
            return command_list
        else:
            return self.get_help(command_string)

    def command_not_recognized(self):
        return "Command not recognized, please try \"$commands\" for available commands"
