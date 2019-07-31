from redis import Redis

from ..command import Command
from ..eventpackage import EventPackage

# a simple command to demonstrate how to connect to redis

# hostname can simply be "redis" because that's the name of the redis container
redis = Redis(host="redis", db=0)

class CountCommand(Command):
    def __init__(self):
        self.name = "$count" # this is required in order for the command to run!
        self.help = "$count | Count for fun!"
        self.author = "spacedog"
        self.last_updated = "July 31, 2019"

    def run(self, event_pack: EventPackage):
        count = redis.incr("command:count:i")
        return "You counted to {}!".format(count)
