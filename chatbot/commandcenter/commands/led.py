from ..command import Command
from ..eventpackage import EventPackage
import requests
import re
from os import environ

# note: this command only works when run on a machine in same subnet as dot.
# (this command will work when run on dot.)

# Modes that ignore color (don't require a hex color argument)
COLORLESS_MODES = ['fire', 'police', 'rainbow', 'off']

ALL_MODES = [
    'color', 'chase', 'rainbow', 'random',
    'solid', 'breathe', 'strobe', 'fire', 'meteor', 'scanner',
    'sparkle', 'police', 'gradient', 'wave', 'candy', 'off'
]

MODE_DESCRIPTIONS = {
    'color':    'color wipe across the strip',
    'chase':    'theater chase animation',
    'rainbow':  'rainbow cycle (no color needed)',
    'random':   'random mode and color each cycle',
    'solid':    'set all pixels to one color instantly',
    'breathe':  'smooth pulsing fade in/out',
    'strobe':   'fast on/off flashing',
    'fire':     'flickering fire simulation (no color needed)',
    'meteor':   'shooting light with fading tail',
    'scanner':  'Knight Rider bouncing light',
    'sparkle':  'random white twinkles over base color',
    'police':   'red/blue alternating flash (no color needed)',
    'gradient': 'smooth gradient to complementary color',
    'wave':     'sinusoidal brightness wave',
    'candy':    'scrolling alternating color segments',
    'off':      'turn all LEDs off',
}

class LedCommand(Command):
    def __init__(self):
        super().__init__()
        self.name = "$led"
        self.help = "$led #rrggbb [mode] | $led off | $led modes | $led help"
        self.author = "spacedog"
        self.last_updated = "February 12th 2026"
        self.yakko_url = environ.get("YAKKO_URL", "")
        self.yakko_api_key = environ.get("YAKKO_API_KEY", "")

    def run(self, event_pack: EventPackage):
        if not self.yakko_url or not self.yakko_api_key:
            return "Error: YAKKO_URL or YAKKO_API_KEY environment variable is not set."

        if len(event_pack.body) < 2:
            return "Usage: $led #rrggbb [mode] — try $led help for all options"

        first_arg = event_pack.body[1].lower()

        # Subcommands
        if first_arg == "help":
            lines = ["$led #rrggbb [mode]  — set LEDs to a color with optional animation",
                      "$led <mode>         — start a colorless mode (fire, police, rainbow, off)",
                      "$led off            — turn all LEDs off",
                      "$led modes          — list all available modes",
                      "$led help           — show this message",
                      "",
                      "Modes:"]
            for mode in ALL_MODES:
                lines.append(f"  {mode:10s} — {MODE_DESCRIPTIONS[mode]}")
            return "\n".join(lines)

        if first_arg == "modes":
            return "Available modes: " + ", ".join(ALL_MODES)

        # Handle colorless modes used directly: $led off, $led fire, etc.
        if first_arg in COLORLESS_MODES:
            data = {"status": {"type": first_arg, "red": 0, "green": 0, "blue": 0}}
            return self._send(data, f"Mode set to: {first_arg}")

        # Try to read color
        color_string = event_pack.body[1]
        if re.match("^#[0-9 a-f A-F]{6}$", color_string) == None:
            return "Invalid color. Usage: $led #rrggbb [mode] — try $led help"

        # valid color
        red = int(color_string[1:3], 16)/2
        green = int(color_string[3:5], 16)/2
        blue = int(color_string[5:7], 16)/2

        data = {
            "status": {
                "red": red,
                "green": green,
                "blue": blue,
            }
        }

        r = "Set color to: " + color_string

        if len(event_pack.body) >= 3:
            typ = event_pack.body[2].lower()
            if typ in ALL_MODES:
                data["status"]["type"] = typ
                r += f" ({typ})"
            else:
                return f"Unknown mode: {typ}. Use $led modes to see available modes."

        return self._send(data, r)

    def _send(self, data, success_msg):
        try:
            response = requests.post(
                self.yakko_url,
                json=data,
                headers={"Authorization": "Bearer " + self.yakko_api_key},
                timeout=5,
            )
            if response.status_code != 200:
                body_snip = (response.text or "").strip().replace("\n", " ")
                if len(body_snip) > 200:
                    body_snip = body_snip[:200] + "..."
                return success_msg + " (server {}: {})".format(response.status_code, body_snip)
            return success_msg
        except Exception as e:
            return success_msg + " (request failed: {})".format(e)
