from ..eventpackage import EventPackage

from redis import Redis
redis = Redis(host="redis", db=0)

# responses that a command can send back up.
class CommandResponse:
    def __init__(self):
        pass

    def __str__(self):
        return "Command Response Base?"

# text responses get sent as text
class CommandTextResponse(CommandResponse):
    def __init__(self, text: str):
        super().__init__()
        self.text = text

    def __str__(self):
        return self.text

    def __len__(self):
        return len(self.text)

# state responses get sent as state changes (e.g. topic changes)
class CommandStateResponse(CommandResponse):
    def __init__(self, event_type: str, content: dict):
        super().__init__()
        self.type = event_type
        self.content = content

    def __str__(self):
        return f"{self.type}: {self.content}"

class Command:
    def __init__(self):
        self.name = "$default_command_object"
        self.help = "...looks like self.help never got defined for " + self.name + "..."
        self.author = "...who knows? (They forgot to set the author value!)"
        self.last_updated = "20XX (No date found)"
        self.raw_db = False
        
        # if true, self.sniff_message() will be invoked for EVERY message.
        self.is_nosy = False

    def __str__(self):
        return self.name

    def run(self, eventpackage: EventPackage):
        return "This command doesn't have an implementation yet!"

    def sniff_message(self, eventpackage: EventPackage):
        pass

    def get_name(self):
        return str(self.name)

    def get_help(self):
        return str(self.help)

    def get_author(self):
        return str(self.author)

    def get_last_updated(self):
        return str(self.last_updated)

    def get_nosy(self):
        if hasattr(self, "is_nosy"):
            return self.is_nosy
        return False

    # ez database api
    def _db_create_namespaced_key(self, key):
        # extracts the command name and returns a namespace to use
        if hasattr(self, 'raw_db') and self.raw_db == True:
            return key
        else:
            return "command:" + self.name[1:] + ":" + key

    def db_set(self, key, value):
        return redis.set(self._db_create_namespaced_key(key), value)

    def db_set_if_not_exists(self, key, value):
        return redis.setnx(self._db_create_namespaced_key(key), value)
    
    def db_get(self, key):
        return redis.get(self._db_create_namespaced_key(key))

    def db_del(self, key):
        return redis.delete(self._db_create_namespaced_key(key))

    def db_incr(self, key):
        return redis.incr(self._db_create_namespaced_key(key))

    def db_incrby(self, key, amount):
        return redis.incrby(self._db_create_namespaced_key(key), amount)
    
    def db_lpush(self, list, value):
        return redis.lpush(self._db_create_namespaced_key(list), value)

    def db_rpush(self, list, value):
        return redis.rpush(self._db_create_namespaced_key(list), value)

    # just aliases for rpush
    def db_append(self, list, value):
        return self.db_rpush(list, value)

    def db_push(self, list, value):
        return self.db_rpush(list, value)

    def db_lpop(self, list):
        return redis.lpop(self._db_create_namespaced_key(list))

    def db_rpop(self, list):
        return redis.rpop(self._db_create_namespaced_key(list))

    # just an alias for rpop
    def db_pop(self, list):
        return self.db_rpop(list)

    def db_list_len(self, list):
        return redis.llen(self._db_create_namespaced_key(list))

    def db_list_set(self, list, index, key):
        return redis.lset(self._db_create_namespaced_key(list), index, key)

    def db_list_rem(self, list, num, key):
        return redis.lrem(self._db_create_namespaced_key(list), num, key)

    def db_list_idx(self, list, index):
        return redis.lindex(self._db_create_namespaced_key(list), index)

    def db_list_range(self, list, start, end):
        return redis.lrange(self._db_create_namespaced_key(list), start, end)

    def db_list_trim(self, list, start, end):
        return redis.ltrim(self._db_create_namespaced_key(list), start, end)
    
    # shortcut to get whole list
    def db_list_get(self, key):
        return self.db_list_range(key, 0, -1)
    
    def db_set_add(self, set, value):
        return redis.sadd(self._db_create_namespaced_key(set), value)

    def db_set_remove(self, set, value):
        return redis.srem(self._db_create_namespaced_key(set), value)

    def db_set_is_member(self, set, key):
        return redis.sismember(self._db_create_namespaced_key(set), key)

    def db_set_get(self, set):
        return redis.smembers(self._db_create_namespaced_key(set))

    def db_set_random_element(self, set):
        return redis.srandmember(self._db_create_namespaced_key(set))

    def db_set_union(self, set_one, set_two):
        return redis.sunion(self._db_create_namespaced_key(set_one), self._db_create_namespaced_key(set_two))

    def db_set_sorted_add(self, set, key, value):
        return redis.zadd(self._db_create_namespaced_key(set), {key: value})

    def db_set_sorted_remove(self, set, value):
        return redis.zrem(self._db_create_namespaced_key(set), value)

    def db_set_sorted_range(self, set, start, end):
        return redis.zrange(self._db_create_namespaced_key(set), start, end)

    def db_set_sorted_get(self, set):
        return self.db_set_sorted_range(self._db_create_namespaced_key(set), 0, -1)
    
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
