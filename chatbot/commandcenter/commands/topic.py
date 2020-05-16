from ..command import Command
from ..eventpackage import EventPackage

class TopicCommand(Command):
    def __init__(self):
        self.name = "$topic"
        self.help = "$topic | modify the current channel topic"
        self.author = "sphinx"
        self.last_updated = "May 16, 2020"
        self.whitelist = ["alu", "spacedog", "sphinx"]

    def run(self, event_pack: EventPackage):
        args = event_pack.body[1:]
        room = event_pack.room_id.split(":")[0][1:]
        nick = event_pack.sender.split(":")[0][1:]

        if len(args) > 0:
            if args[0][0] == "-" and len(args[0]) == 2:
                switch = args[0][1].lower()

                # admin check
                if not nick in self.whitelist:
                    return ("ERR", "USER NOT IN WHITELIST")

                # delete some topic
                if switch == "d":
                    if len(args) > 1:
                        try:
                            index = int(args[1])
                        except ValueError:
                            return ("ERR", "INDEX NOT AN INTEGER")

                        # delete topic at specific index...
                        self._delete_at(room, index)
                    else:
                        # ...or delete last (presumably oldest) topic
                        self._delete_last(room)
                    # update topic
                    return ("TOP", self._get_topic(room))
                # refresh the current topic (possibly edited manually)
                elif switch == "r":
                    return ("TOP", self._get_topic(room))
                # approve proposal
                elif switch == "y":
                    proposed = self.db_get(room + ":proposed")
                    if proposed is not None:
                        self.db_del(room + ":proposed")
                        add = str(proposed, "UTF-8")
                        self.db_lpush(room, add)
                        return ("TOP", self._get_topic(room))
                    else:
                        return ("ERR", "NO TOPIC PROPOSED")
                # disapprove proposal
                elif switch == "n":
                    self.db_del(room + ":proposed")
                    return ("ERR", "PROPOSAL REMOVED")
                # show proposed topic
                elif switch == "p":
                    proposed = self.db_get(room + ":proposed")
                    if proposed is not None:
                        add = str(proposed, "UTF-8")
                        return ("MSG", "topic proposed, awaiting approval: {}".format(add))
                    else:
                        return ("ERR", "NO TOPIC PROPOSED")
                # given switch is unknown
                else:
                    return ("ERR", "UNKNOWN SWITCH {}".format(args[0]))
            else:
                # join up all the arguments, it is the new topic
                add = " ".join(args)

                # if user is in whitelist, just add topic
                if nick in self.whitelist:
                    self.db_lpush(room, add)
                    return ("TOP", self._get_topic(room))
                # otherwise propose topic
                else:
                    self.db_set(room + ":proposed", add)
                    return ("MSG", "topic proposed, awaiting approval: {}".format(add))

        else:
            return ("ERR", "NO ARGUMENTS GIVEN")

    # obtain topic list from redis, delimit with pipes
    def _get_topic(self, room):
        return " | ".join(str(x, "UTF-8") for x in self.db_list_get(room))

    # delete topic from a specific index
    def _delete_at(self, room, index):
        self.db_list_set(room, index, "__DELETED__")
        self.db_list_rem(room, 1, "__DELETED__")

    # delete the last (presumably oldest) topic
    def _delete_last(self, room):
        self.db_list_trim(room, 0, -2)
