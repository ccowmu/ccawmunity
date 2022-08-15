from ..command import Command
from ..command import CommandCodeResponse
from ..command import CommandTextResponse
from ..command import CommandRainbowResponse
from ..command import CommandBigResponse
from ..eventpackage import EventPackage
from ..commander import commander

import random
import math

class Rainbow(Command):
    def __init__(self):
        super().__init__()
        self.name = "$rainbow"
        self.help = "$rainbow | Take your boring, colorless command output, and make it Gay! | Usage: $rainbow <$command (with or without the $)>"
        self.author = "bluebell"
        self.last_updated = "Aug. 14, 2022"
        self.aliases = ["$gay"]

    def run(self, event_pack: EventPackage):
        if len(event_pack.body) >= 2:
            body = event_pack.body[1:]
        else:
            length = random.randint(3,20)
            output = ""
            for i in range(3, length):
                 output += str(random.choice('oO'))
            return CommandRainbowResponse(self.textToHtmlRainbow(output))

        subcommand = body[0]
        if  subcommand[0] != '$':
            subcommand = '$'+ subcommand

        if subcommand == "$rainbow":
            return "Stop that! >:("

        event_pack.body = body
        my_commander = commander.Commander()
        subcommand_response = my_commander.run_command(subcommand, event_pack)
        if isinstance(subcommand_response, str):
            if not self.check_rainbow(subcommand_response):
                if "not recognized" in subcommand_response:
                    # not a command, just echo the body
                    return CommandRainbowResponse(self.textToHtmlRainbow(" ".join(body)))
                else:
                    return CommandRainbowResponse(self.textToHtmlRainbow(subcommand_response))
            else:
                return "Stop that! >:("
        elif isinstance(subcommand_response, CommandTextResponse):
            if self.check_rainbow(subcommand_response.text) or hasattr(subcommand_response, "htmlText"):
                return "Stop that! >:("
            elif subcommand_response.is_code:
                text = subcommand_response.text
                if "<h1>" in text and "</h1>" in text:
                    text = text.replace("<h1>","")
                    text = text.replace("</h1>","")
                    text = self.textToHtmlRainbow(text)
                    text = "<h1>" + text + "</h1>"
                return CommandCodeResponse(text)
            elif subcommand_response.is_big:
                text = subcommand_response.text
                return CommandBigResponse(self.textToHtmlRainbow(text))
            else:
                return CommandRainbowResponse(self.textToHtmlRainbow(subcommand_response.text))
        else:
            return f"ERROR | {subcommand} does not output a plain text response!"


    def textToHtmlRainbow(self, text):
        textlen = len(text)
        frequency = (2 * math.pi) / textlen
        output = ""
        for i in range(textlen):
            # no need to change color on whitespace
            if text[i] == " ":
                output = output + " "
                continue
            # math wizardry to map character position in string to CIELAB color space
            a = 127 * math.cos(i * frequency)
            b = 127 * math.sin(i * frequency)
            rgb = self.labToRGB(75, a, b)
            red = f'{rgb[0]:x}'.zfill(2)
            green = f'{rgb[1]:x}'.zfill(2)
            blue = f'{rgb[2]:x}'.zfill(2)
            output = output + '<font color="#{}{}{}">{}</font>'.format(red,green,blue,text[i])
        return output



    def labToRGB(self, l, a, b):
        # more math wizardry to convert CIELAB color to CIEXYZ color as an intermediate step
        y = (l + 16) / 116
        x = self.adjustXYZ(y + a / 500) * 0.9505
        z = self.adjustXYZ(y - b / 200) * 1.089
        y = self.adjustXYZ(y)

        # linear transformation from CIEXYZ to RGB
        red = 3.24096994*x - 1.53738318*y - 0.49861076*z
        green = -0.96924364*x + 1.8759675*y + 0.04155506*z
        blue = 0.05563008*x - 0.20397696*y + 1.05697151*z

        return [self.adjustRGB(red), self.adjustRGB(green), self.adjustRGB(blue)]

    def adjustXYZ(self, v):
        if v > 0.2069:
            return v**3
        return 0.1284 * v - 0.01771

    def gammaCorrection(self, v):
        if v <= 0.0031308:
            return 12.92 * v
        return 1.055 * v**(1/2.4) - 0.055

    def adjustRGB(self, v):
        corrected = self.gammaCorrection(v)

        limited = min(max(corrected, 0), 1)

        return round(limited * 255)

    def check_rainbow(self, text):
        return "<font" in text
