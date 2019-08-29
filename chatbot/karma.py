import re

from redis import Redis
redis = Redis(host="redis", db=0)

regex = re.compile(r"([^\-\$ ]+|(?:\().+?(?:\)))(\+\+|--)")

def create_namespace(key):
    return "karma:" + str(key)

def process_message(message):
    matches = regex.findall(message)

    for tup in matches:
        key = tup[0]

        if key[0] == "(" and key[-1:] == ")":
            key = key[1:-1] # chop off parenthesis

        op = tup[1]

        # keep a set of all items
        redis.sadd("karma:all_items", key)

        if op == "++":
            redis.incr("karma:" + str(key))
        elif op == "--":
            redis.incr("karma:" + str(key), -1)
