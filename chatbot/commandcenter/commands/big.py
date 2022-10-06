from ..command import Command
from ..command import CommandCodeResponse
from ..command import CommandTextResponse
from ..command import CommandRainbowResponse
from ..command import CommandBigResponse
from ..eventpackage import EventPackage
from ..commander import commander

import random

class Big(Command):
    def __init__(self):
        super().__init__()
        self.name = "$big"
        self.help = "$big | Take some text, make it big! | Usage: $big <$command (with or without the $)>"
        self.author = "bluebell"
        self.last_updated = "Aug. 14, 2022"


    def run(self, event_pack: EventPackage):
        if len(event_pack.body) >= 2:
            body = event_pack.body[1:]
        else:
            length = random.randint(3,20)
            output = ""
            for i in range(3, length):
                 output += str(random.choice('oO'))
            return CommandBigResponse(output)

        subcommand = body[0]
        if  subcommand[0] != '$':
            subcommand = '$'+ subcommand

        if subcommand == "$big":
            return "Too big! >:("

        event_pack.body = body
        my_commander = commander.Commander()
        subcommand_response = my_commander.run_command(subcommand, event_pack)
        if isinstance(subcommand_response, str):
            if "not recognized" in subcommand_response:
                # not a command, treat the args as text to be echoed
                return CommandBigResponse(" ".join(body))
            else:
                return CommandBigResponse(subcommand_response)
        elif isinstance(subcommand_response, CommandTextResponse):
            if subcommand_response.is_code:
                big_text = "<h1>" + subcommand_response.text + "</h1>"
                return CommandCodeResponse(big_text)
            elif subcommand_response.is_big:
                return "Stop that! >:("
            else:
                return CommandBigResponse(subcommand_response.text)
        else:
            return f"ERROR | {subcommand} does not output a plain text response!"
