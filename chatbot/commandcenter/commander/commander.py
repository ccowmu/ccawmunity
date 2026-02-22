import multiprocessing
import re

from os import listdir
from os.path import isfile, join, abspath, dirname

# important! this is where we discover all of the commands in the command directory.
# if this isn't called, Command.__subclasses__() is empty.
from ..commands import *
from .builtin import *

from ..command import Command
from ..command import CommandCodeResponse
from ..eventpackage import EventPackage

class Commander:
    def __init__(self, prefix = "$", timeout = 3):
        self.commands = {}
        self.alias_map = {}
        self.prefix = prefix
        self.timeout = timeout
        self.command_names = []
        print("Prefix: " + self.prefix)

        for command_class in Command.__subclasses__():
            command = command_class()
            command_name = command.get_name()
            self.commands[command_name] = command
            self.command_names.append(command_name)

            # map command aliases to initialized command objects, and add them to the list of names
            command_aliases = command.get_aliases()
            if command_aliases:
                for alias in command_aliases:
                    self.alias_map[alias] = command_name

        print("Commander loaded with commands:")
        print(self.get_help_all())

    def is_command(self, line):
        if line[0:len(self.prefix)] != self.prefix:
            # doesn't start with command prefix
            return False

        if re.match(r"\$\d+", line):
            # just a dollar amount, not a command
            return False

        return True

    def run_command(self, command_string, event_pack: EventPackage):
        if self.is_command(command_string):
            # convert command string to use $ as prefix in order to work with the internal syntax
            command_string_normalized = command_string.replace(self.prefix, "$")

            # print("Commander: running command: {0}".format(command_string_normalized))

            if command_string_normalized == "$commands":
                print("Built in command: $commands")
                return self.get_help_all()

            if command_string_normalized == "$help":
                print("Built in command: $help")
                if len(event_pack.body) >= 2:
                    return self.get_help(event_pack.body[1].replace(self.prefix, "$"))
                else:
                    return self.get_help_all()

            if command_string_normalized == "$info" or command_string_normalized == "$blame":
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
            elif command_string_normalized in self.alias_map:
                real_command_name = self.alias_map[command_string_normalized]
                command = self.commands[real_command_name]

                # lazily copying the code from the first case because refactoring is hard

                recv_end, send_end = multiprocessing.Pipe(False)

                p = multiprocessing.Process(target=self.start_command_process, args=(command, event_pack, send_end))

                p.start()
                p.join(self.timeout)

                if p.is_alive():
                    print(f"Commander: killing a command after timeout. ({self.timeout} seconds)")
                    p.terminate()
                    return self.command_timed_out(command.get_name())

                return recv_end.recv()
            else:
                return self.command_not_recognized()
        else:
            # not a command, pass on to nosy commands
            for name, command in self.commands.items():
                if command.get_nosy():
                    try:
                        command.sniff_message(event_pack)
                    except Exception as e:
                        print(f"WARNING | {name}'s sniff threw an exception: {e}")
            return None

    def start_command_process(self, command, event_pack, pipe):
        # encapsulated in a new function so that the commands can still use "return" to send their chat strings back.
        # they will never know the evil that lies within the commander
        try:
            pipe.send(command.run(event_pack))
        except Exception as e:
            pipe.send("{} failed. Reason: {}".format(command.get_name(), e))

    def get_help(self, command_string):
        command_string = self.add_prefix(command_string)
        if command_string in self.commands:
            return self.commands[command_string].get_help().replace("$", self.prefix)
        else:
            return self.command_not_recognized()

    def get_info(self, command_string):
        command_string = self.add_prefix(command_string)
        if command_string in self.commands:
            command = self.commands[command_string]
            output = "Info for " + command_string.replace("$", self.prefix) + "...\n"
            output += "Last updated: " + command.get_last_updated() + "\n"
            output += "Author: " + command.get_author() + "\n"
            return output
        else:
            return self.command_not_recognized()

    def add_prefix(self, command_string):
        if command_string[0] == self.prefix:
            # prefix is already there, nothing to do
            return command_string
        else:
            return self.prefix + command_string

    def get_help_all(self):
        command_list = ""
        for label in self.commands:
            command_list += self.get_help(label) + "\n"
        return CommandCodeResponse(command_list)

    def command_not_recognized(self):
        return "Command not recognized, please try \"$help\" for available commands".replace("$", self.prefix)

    def command_timed_out(self, command_string):
        return f"{command_string} timed out. (Command time limit is {self.timeout} seconds.)"

    def get_command_names(self):
        return self.command_names
