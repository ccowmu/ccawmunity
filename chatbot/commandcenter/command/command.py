from ..eventpackage import EventPackage

import redis

class Command:
    db_conn = None

    def __init__(self):
        self.name = "$default_command_object"
        self.help = "...looks like self.help never got defined for " + self.name + "..."
        self.author = "...who knows? (They forgot to set the author value!)"
        self.last_updated = "20XX (No date found)"

    def __str__(self):
        return self.name

    def _connect_to_db(self):
        if not self.db_conn:
            self.db_conn = redis.Redis(host='localhost', port=6379, decode_responses=True)
        return self.db_conn

    def run(self, eventpackage: EventPackage):
        return "This command doesn't have an implementation yet!"

    def get_name(self):
        return str(self.name)

    def get_help(self):
        return str(self.help)

    def get_author(self):
        return str(self.author)

    def get_last_updated(self):
        return str(self.last_updated)

    def kv_get(self, field):
        r = self._connect_to_db()
        print("Trying to get " + self.name + " " + field)
        return r.hget(self.name, field)

    def kv_set(self, field, value):
        r = self._connect_to_db()
        print("Trying to set " + self.name + " " + field + " to " + value)
        return r.hset(self.name, field, value)
