from ..command import Command
from ..eventpackage import EventPackage
import requests
from os import environ

class LetMeInCommand(Command):
    def __init__(self):
        super().__init__()
        self.name = "$letmein"
        self.help = "$letmein [sound.wav] | Unlocks the door. Optionally specify a sound to play."
        self.author = "Lochlan McElroy"
        self.last_updated = "February 2nd 2026"
        self.yakko_url = environ.get("YAKKO_URL", "")
        self.yakko_api_key = environ.get("YAKKO_API_KEY", "")

    def run(self, event_pack: EventPackage):
        if not self.yakko_url or not self.yakko_api_key:
            return "Error: YAKKO_URL or YAKKO_API_KEY environment variable is not set."

        if len(event_pack.body) < 1:
            return "Usage: $letmein"

        headers = {"Authorization": "Bearer " + self.yakko_api_key}

        # Subcommands (don't unlock)
        if len(event_pack.body) > 1:
            sub = event_pack.body[1].lower()
            if sub == "help":
                return (
                    "$letmein            — unlock the door (random sound)\n"
                    "$letmein <sound>    — unlock and play a specific sound\n"
                    "$letmein sounds     — list available sounds\n"
                    "$letmein help       — show this message"
                )
            if sub == "sounds":
                return self.list_sounds(headers)

        sound = event_pack.body[1] if len(event_pack.body) > 1 else ""

        # Validate sound exists before unlocking
        if sound:
            try:
                status = requests.get(self.yakko_url, headers=headers, timeout=5)
                available = status.json().get('sounds', [])
                if available and sound not in available:
                    return "Sound not found: {}. Use $letmein sounds to see available sounds.".format(sound)
            except Exception:
                pass  # if we can't check, let it through

        try:
            data = {
                "status": {
                    "letmein": True,
                    "sound": sound
                }
            }
            response = requests.post(
                self.yakko_url,
                json=data,
                headers=headers,
                timeout=5,
            )

            if response.status_code == 200:
                if sound:
                    return f"Door unlocked! Playing {sound}"
                return "Door unlocked!"

            else:
                body_snip = (response.text or "").strip().replace("\n", " ")
                if len(body_snip) > 200:
                    body_snip = body_snip[:200] + "..."
                return (
                    "Failed to unlock the door. Server returned status code {}: {}."
                ).format(response.status_code, body_snip)

        except Exception as e:
            print("Error sending request: {}".format(e))
            return "An error occurred while attempting to unlock the door: {}.".format(e)

    def list_sounds(self, headers):
        try:
            response = requests.get(self.yakko_url, headers=headers, timeout=5)
            response.raise_for_status()
            sounds = response.json().get('sounds', [])
            if not sounds:
                return "No sounds available yet (doorbot hasn't synced its list)."
            return "Available sounds ({}):\n{}".format(len(sounds), "\n".join("  " + s for s in sounds))
        except Exception as e:
            return "Error fetching sound list: {}".format(e)
