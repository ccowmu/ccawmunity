from ..command import Command
from ..command import CommandCodeResponse
from ..command import CommandTextResponse
from ..command import CommandRainbowResponse
from ..eventpackage import EventPackage
from ..commander import commander

import random
import math

class RandDong(Command):
    def __init__(self):
        self.name = "$rainbow"
        self.help = "$rainbow | Take your boring, colorless command output, and make it Gay! | Usage: $rainbow <$command (with or without the $)>"
        self.author = "bluebell"
        self.last_updated = "Aug. 6, 2022"


    def run(self, event_pack: EventPackage):
        if len(event_pack.body) >= 2:
            body = event_pack.body[1:]
        else:
            return "ERROR | Not enough args! Usage: $rainbow <$command (with or without the $)>"

        if  body[0][0] != '$':
            body[0] = '$'+ body[0]

        if body[0] == "$rainbow":
            return "Nice try, wise guy."

        event_pack.body = body
        my_commander = commander.Commander()
        boring_colorless_command_response = my_commander.run_command(body[0], event_pack)

        if ((isinstance(boring_colorless_command_response, CommandTextResponse) 
             and not isinstance(boring_colorless_command_response, CommandCodeResponse) 
             and not isinstance(boring_colorless_command_response, CommandRainbowResponse))
           or isinstance(boring_colorless_command_response, str)):
            gay = CommandRainbowResponse(boring_colorless_command_response)
            return gay
        else:
            return f"ERROR | {body[0]} does not output a plain text response!"
