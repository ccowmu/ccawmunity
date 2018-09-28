import sys
import importlib

from os import listdir
from os.path import isfile, join, abspath, dirname

from ..commands import *
from ..command import Command

class Commander:
    def __init__(self):
        self.commands = []

        for command_class in Command.__subclasses__():
            command = command_class()
            self.commands.append(command)
            print("Loaded command: " + command.get_name())

    def run_command(self, command: Command):
        if command in self.commands:
            return command.run() # PLACEHOLDER - incorrect args here...
        else:
            return "Command not recognized, please try \"$commands\" for available commands"
            
    def get_help(self, command: Command):
        if command in self.commands:
            return command.get_help()
        else:
            return "Command not recognized, please try \"$commands\" for available commands"

    def get_help_string(self):
        command_list = ""
        for command in self.commands:
            command_list += command.get_help() + '\n'
        return command_list

    def get_commands_string(self):
        help_list = ""
        for command in self.commands:
            help_list += command.get_name() + '\n'
        return help_list