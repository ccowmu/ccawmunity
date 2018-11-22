# Github Listener
# By spacedog
# Sends information about events that happen in the ccawmunity repository.

from ..listener import Listener

class GithubListener(Listener):
    def __init__(self):
        super().__init__() # important!
        self.name = "l_github_ccawmunity" # name of the listener.

        # list of rooms that this listener is allowed to post in
        self.rooms = [
            '#ccawmunity:cclub.cs.wmich.edu'
        ]

        self.identity = '[repository][full_name] = ccowmu/ccawmunity'

    def process(self, body):
        output_str = ""
        
        if "issue" in body:
            # an issue event
            if body["action"] == "opened" or body["action"] == "reopened":
                # an issue was opened/reopened
                output_str  = "New issue in " + body["repository"]["name"] + ": " + body["issue"]["title"] + "\n"
                output_str += body["issue"]["html_url"]
        elif "pull_request" in body:
            # a pull request event
            output_str  = "@room:\n" 
            output_str += "New pull request in " + body["repository"]["name"] + ": " + body["pull_request"]["title"] + "\n"
            output_str += body["pull_request"]["html_url"]

        return output_str
