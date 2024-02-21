from ..command import Command
from ..eventpackage import EventPackage
from .github_token import BEARER_TOKEN
import requests

class GitAddCommand(Command):
    def __init__(self):
        super().__init__()

        self.name = "$git_add"
        self.help = "$git_add | Adds a user to the ccowmu github by email | Usage: $git_add <email>"
        self.author = "bmo"
        self.last_updated = "Feb 19, 2024"
        
        self.base_url = "https://api.github.com/orgs/ccowmu/invitations"
        self.headers = {
            'Accept': 'application/vnd.github+json',
            'Authorization': f'Bearer {BEARER_TOKEN}',
            'X-GitHub-Api-Version': '2022-11-28'
        }
        self.data = {
            'role': 'direct_member'
        }

    def run(self, event_pack: EventPackage):
        # should always receive 2 args
        if len(event_pack.body) == 2:
            self.data['email'] = event_pack.body[1]

            response = requests.post(self.base_url, headers=self.headers, json=self.data)

            if not response.ok:
                return f'Failed to send invitation: {response.status_code} - {response.text}'

            return "Invitation sent"
        else:
            return "Invalid input: Usage: $git_add <email>"
            