from ..eventpackage import EventPackage

from redis import Redis
redis = Redis(host="redis", db=0)

class Command:
    def __init__(self):
        self.name = "$default_command_object"
        self.help = "...looks like self.help never got defined for " + self.name + "..."
        self.author = "...who knows? (They forgot to set the author value!)"
        self.last_updated = "20XX (No date found)"

    def __str__(self):
        return self.name

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

    # ez database api
    def _db_create_namespaced_key(self, key):
        # extracts the command name and returns a namespace to use
        return "command:" + self.name[1:] + ":" + key

    def db_set(self, key, value):
        return redis.set(self._db_create_namespaced_key(key), value)

    def db_set_if_not_exists(self, key, value):
        return redis.setnx(self._db_create_namespaced_key(key), value)
    
    def db_get(self, key):
        return redis.get(self._db_create_namespaced_key(key))

    def db_incr(self, key):
        return redis.incr(self._db_create_namespaced_key(key))

    def db_incrby(self, key, amount):
        return redis.incrby(self._db_create_namespaced_key(key), amount)
    
    def db_lpush(self, key, value):
        return redis.lpush(self._db_create_namespaced_key(key), value)

    def db_rpush(self, key, value):
        return redis.rpush(self._db_create_namespaced_key(key), value)

    # just aliases for rpush
    def db_append(self, key, value):
        return self.db_rpush(key, value)

    def db_push(self, key, value):
        return self.db_rpush(key, value)

    def db_lpop(self, key):
        return redis.lpop(self._db_create_namespaced_key(key))

    def db_rpop(self, key):
        return redis.rpop(self._db_create_namespaced_key(key))

    # just an alias for rpop
    def db_pop(self, key):
        return self.db_rpop(key)

    def db_list_len(self, key):
        return redis.llen(self._db_create_namespaced_key(key))

    def db_list_range(self, key, start, end):
        return redis.lrange(self._db_create_namespaced_key(key), start, end)

    # shortcut to get whole list
    def db_get_list(self, key):
        return self.db_list_range(key, 0, -1)
    
    def db_set_add(self, key, value):
        return redis.sadd(self._db_create_namespaced_key(key), value)

    def db_set_remove(self, key):
        return redis.srem(self._db_create_namespaced_key(key))

    def db_set_is_member(self, key, set):
        return redis.sismember(self._db_create_namespaced_key(set), self._db_create_namespaced_key(key))

    def db_set_get(self, key):
        return redis.smembers(self._db_create_namespaced_key(key))

    def db_set_union(self, set_one, set_two):
        return redis.sunion(self._db_create_namespaced_key(set_one), self._db_create_namespaced_key(set_two))
    
    def db_hash_set(self, object, key, value):
        return redis.hset(self._db_create_namespaced_key(object), key, value)

    def db_hash_get(self, object, key):
        return redis.hget(self._db_create_namespaced_key(object), key)

    def db_hash_get_all(self, object):
        return redis.hgetall(self._db_create_namespaced_key(object))

    def db_hash_incrby(self, object, key, amount):
        return redis.hincrby(self._db_create_namespaced_key(object), key, amount)

    def db_hash_incr(self, object, key):
        return self.db_hash_incrby(object, key, 1)

    def db_hash_del(self, object, key):
        return redis.hdel(self._db_create_namespaced_key(object), key)
