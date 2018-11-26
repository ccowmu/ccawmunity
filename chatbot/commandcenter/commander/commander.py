import sys
import importlib
import multiprocessing

from os import listdir
from os.path import isfile, join, abspath, dirname

# important! this is where we discover all of the commands in the command directory.
# if this isn't called, Command.__subclasses__() is empty.
from ..commands import *
from .builtin import *

from ..command import Command
from ..eventpackage import EventPackage

class Commander:
    def __init__(self, prefix = "$", timeout = 3):
        self.commands = {}
        self.prefix = prefix
        self.timeout = timeout

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
            command = self.commands[command_string_normalized]

            # create a pipe to retrieve the result
            recv_end, send_end = multiprocessing.Pipe(False)

            # start the command on a new process
            p = multiprocessing.Process(target=self.start_command_process, args=(command, event_pack, send_end))

            # start the process, timeout after self.timeout seconds
            p.start()
            p.join(self.timeout)

            # if the process is still alive after self.timeout seconds, kill it
            if p.is_alive():
                print(f"Commander: killing a command after timeout. ({self.timeout} seconds)")
                # NOTE:
                # terminating the process corrupts the pipe created above. 
                # this is fine as long as we don't use it again.
                p.terminate() 
                return self.command_timed_out(command.get_name())

            # if the process wasn't terminated, it's return result will be in the pipe.
            return recv_end.recv()
        else:
            return self.command_not_recognized()

    def start_command_process(self, command, event_pack, pipe):
        # encapsulated in a new function so that the commands can still use "return" to send their chat strings back.
        # they will never know the evil that lies within the commander
        try:
            pipe.send(command.run(event_pack))
        except Exception as e:
            pipe.send("{} failed. Reason: {}".format(command.get_name(), e))
            
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

    def command_timed_out(self, command_string):
        return f"{command_string} timed out. (Command time limit is {self.timeout} seconds.)"
