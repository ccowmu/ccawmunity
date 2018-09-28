import sys
import importlib

from os import listdir
from os.path import isfile, join, abspath, dirname

from ..commands import *
from ..command import Command
from ..eventpackage import EventPackage

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

        if command_string in self.commands:
            try:
                command = self.commands[command_string]
                return command.run(event_pack)
            except:
                return "YA DID IT WRONG."
        else:
            return "Command not recognized, please try \"$commands\" for available commands"
            
    def get_help(self, command_string):
        if command_string in self.commands:
            return self.commands[command_string].get_help()
        else:
            return "Command not recognized, please try \"$commands\" for available commands"

    def get_help_string(self, command_string = ''):
        if command_string == '':
            command_list = ""
            for label in self.commands:
                command = self.commands[label]
                command_list += command.get_help() + '\n'
            return command_list
        else:
            return self.get_help(command_string)
