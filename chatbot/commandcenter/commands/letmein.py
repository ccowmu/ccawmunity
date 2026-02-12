from ..command import Command
from ..eventpackage import EventPackage
import requests
from os import environ
from datetime import datetime

class LetMeInCommand(Command):
    def __init__(self):
        super().__init__()
        self.name = "$letmein"
        self.help = "$letmein [sound] | $letmein sneaky | $letmein sounds | $letmein log | $letmein status | $letmein help"
        self.author = "Lochlan McElroy"
        self.last_updated = "February 12th 2026"
        self.yakko_url = environ.get("YAKKO_URL", "")
        self.yakko_api_key = environ.get("YAKKO_API_KEY", "")

    def run(self, event_pack: EventPackage):
        if not self.yakko_url or not self.yakko_api_key:
            return "Error: YAKKO_URL or YAKKO_API_KEY environment variable is not set."

        if len(event_pack.body) < 1:
            return "Usage: $letmein — try $letmein help for all options"

        headers = {"Authorization": "Bearer " + self.yakko_api_key}

        # Subcommands (don't unlock)
        if len(event_pack.body) > 1:
            sub = event_pack.body[1].lower()
            if sub == "help":
                return (
                    "$letmein            — unlock the door (random sound)\n"
                    "$letmein <sound>    — unlock and play a specific sound\n"
                    "$letmein sneaky     — unlock silently (no sound)\n"
                    "$letmein sounds     — list available sounds\n"
                    "$letmein log        — show recent unlock history\n"
                    "$letmein status     — show doorbot health and status\n"
                    "$letmein help       — show this message"
                )
            if sub == "sounds":
                return self.list_sounds(headers)
            if sub == "log":
                return self.show_log(headers)
            if sub == "status":
                return self.show_status(headers)

        sound = event_pack.body[1] if len(event_pack.body) > 1 else ""

        # $letmein sneaky = unlock silently (no sound)
        if sound.lower() == "sneaky":
            sound = "none"

        # Validate sound exists before unlocking (skip for "none")
        if sound and sound != "none":
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
                    "sound": sound,
                    "sender": event_pack.sender,
                }
            }
            response = requests.post(
                self.yakko_url,
                json=data,
                headers=headers,
                timeout=5,
            )

            if response.status_code == 200:
                if sound == "none":
                    return "Door unlocked! (sneaky)"
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
            return "Available sounds ({}):\n{}".format(len(sounds), "\n".join("  " + s for s in sorted(sounds)))
        except Exception as e:
            return "Error fetching sound list: {}".format(e)

    def show_log(self, headers):
        try:
            response = requests.get(self.yakko_url + "/log", headers=headers, timeout=5)
            response.raise_for_status()
            events = response.json()
            if not events:
                return "No unlock events recorded yet."
            # Show last 10 events, most recent first
            recent = events[-10:]
            recent.reverse()
            lines = [f"Recent unlocks ({len(events)} total):"]
            for e in recent:
                ts = e.get('timestamp', '?')
                sender = e.get('sender', 'unknown')
                # Clean up Matrix usernames for readability
                if sender and sender.startswith('@'):
                    sender = sender.split(':')[0][1:]  # @user:server -> user
                sound = e.get('sound', '?')
                lines.append(f"  {ts} — {sender} ({sound})")
            return "\n".join(lines)
        except Exception as e:
            return "Error fetching unlock log: {}".format(e)

    def show_status(self, headers):
        try:
            response = requests.get(self.yakko_url + "/health/doorbot", headers=headers, timeout=5)
            if response.status_code == 404:
                return "Doorbot hasn't sent a heartbeat yet — it may be offline."
            response.raise_for_status()
            data = response.json()

            uptime_s = data.get('uptime_seconds', 0)
            hours, remainder = divmod(uptime_s, 3600)
            minutes, seconds = divmod(remainder, 60)
            if hours > 0:
                uptime_str = f"{hours}h {minutes}m"
            elif minutes > 0:
                uptime_str = f"{minutes}m {seconds}s"
            else:
                uptime_str = f"{seconds}s"

            lines = ["Doorbot Status:"]
            lines.append(f"  Uptime: {uptime_str}")
            lines.append(f"  Last heartbeat: {data.get('timestamp', '?')}")
            last_unlock = data.get('last_unlock')
            lines.append(f"  Last unlock: {last_unlock or 'none this session'}")
            cpu = data.get('cpu_temp_c')
            if cpu is not None:
                lines.append(f"  CPU temp: {cpu}°C")
            mem = data.get('memory_used_pct')
            if mem is not None:
                lines.append(f"  Memory: {mem}% used")
            return "\n".join(lines)
        except Exception as e:
            return "Error fetching doorbot status: {}".format(e)
