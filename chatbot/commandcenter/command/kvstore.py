import redis

class KVStore:
    db_conn = None

    def _connect_to_db(self):
        if not self.db_conn:
            self.db_conn = redis.Redis(host='localhost', port=6379, decode_responses=True)
        return self.db_conn

    def kv_get(self, field):
        r = self._connect_to_db()
        print("Trying to get " + self.name + " " + field)
        return r.hget(self.name, field)

    def kv_set(self, field, value):
        r = self._connect_to_db()
        print("Trying to set " + self.name + " " + field + " to " + value)
        return r.hset(self.name, field, value)
