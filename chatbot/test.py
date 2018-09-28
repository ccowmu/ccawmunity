#!/usr/bin/python3

from commands.commander import Commander

c = Commander()
c.load_commands_from_directory("./commands")
print(c.get_loaded_commands())