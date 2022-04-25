from ..command import Command
from ..command import CommandCodeResponse
from ..eventpackage import EventPackage

import ldap3
import ssl
import string
import time
from datetime import date
from os import environ

class ExpiryCommand(Command):
    def __init__(self):
        self.name = "$expiry"
        self.help = "$expiry | Gets a member's expiration date from their UID. | Usage: $expiry dolphin"
        self.author = "nothingbutflowers, sphinx"
        self.last_updated = "Jan. 26, 2021"
        self.whitelist = ["alu", "zathras", "sphinx", "acp_"]

    def run(self, event_pack: EventPackage):
        # TODO: redo the logic here so code is not repeated, I tried and failed
        LDAP_URL = 'ldap://yakko.cs.wmich.edu:389'
        MEMBER_BASE = 'cn=members,dc=yakko,dc=cs,dc=wmich,dc=edu'
        POSIX_DAY = 86400
        DESIRED_FIELDS = ["shadowExpire"]
        
        tls_config = ldap3.Tls(validate=ssl.CERT_REQUIRED)
        server = ldap3.Server(LDAP_URL)
        conn = ldap3.Connection(server, user="cn=readonly,dc=yakko,dc=cs,dc=wmich,dc=edu", password=environ["LDAP_PASSWORD"], auto_bind="NONE")

        conn.open()
        conn.start_tls()
        conn.bind()

        args = event_pack.body[1:]
        nick = event_pack.sender.split(":")[0][1:]

        if len(args) == 0:
            # no args given, assume sender wants own expiry
            try:
                preparedQuery = "(uid=" + nick + ")"
                conn.search(search_base=MEMBER_BASE,
                            search_filter=preparedQuery, attributes=DESIRED_FIELDS)
                result = conn.entries[0]
                if result["shadowExpire"].value == None:
                    # user doesn't expire
                    return "{} doesn't expire!".format(nick)
                unix_timestamp = result["shadowExpire"].value * POSIX_DAY
                return "{}: {}".format(nick, str(date.fromtimestamp(unix_timestamp).strftime('%Y-%m-%d')))
            except Exception as e:
                print("something went wrong:", e)
                return "this error message is incredibly helpful!"
            finally:
                conn.unbind()
        else:
            # check if arg is "-a" for all
            if args[0] == "-a":
                if nick in self.whitelist:
                    try:
                        preparedQuery = "(shadowExpire<=" + str(int(time.time()) // 86400) + ")"
                        print(preparedQuery)
                        conn.search(search_base=MEMBER_BASE,
                                    search_filter=preparedQuery, attributes=["uid", "shadowExpire"])
                        expiries = []
                        for e in conn.entries:
                            unix_timestamp = e["shadowExpire"].value * POSIX_DAY
                            str_timestamp = str(date.fromtimestamp(unix_timestamp).strftime('%Y-%m-%d'))
                            expiries.append(tuple((e["uid"].value, str_timestamp)))
                        expiries = sorted(expiries, key=lambda x: x[0])

                        result = ""
                        for e in expiries:
                            result += "{}: {}\n".format(e[0], e[1])
                        return CommandCodeResponse(result)
                    except Exception as e:
                        print("aww fuck, I can't believe you've done this:", e)
                    finally:
                        conn.unbind()
            else:
            # assume argument is a nick
                try:
                    preparedQuery = "(uid=" + args[0] + ")"
                    conn.search(search_base=MEMBER_BASE,
                                search_filter=preparedQuery, attributes=DESIRED_FIELDS)
                    result = conn.entries[0]
                    if result["shadowExpire"].value == None:
                        # user doesn't expire
                        return "{} doesn't expire!".format(args[0])
                    unix_timestamp = result["shadowExpire"].value * POSIX_DAY
                    return "{}: {}".format(args[0], str(date.fromtimestamp(unix_timestamp).strftime('%Y-%m-%d')))
                except IndexError as e:
                    return "I don't know who {} is!".format(args[0])
                except Exception as e:
                    print("something went wrong:", e)
                    return "this error message is incredibly helpful!"
                finally:
                    conn.unbind()
        
        # TODO: where should these errors go now?
        # if len(event_pack.body) < 2:
        #     return "Invalid usage of $expiry: not enough arguments. usage: $expiry dolphin"
        # if len(event_pack.body) > 2:
        #     return "Invalid usage of $expiry: too many arguments. $expiry does not support multiple lookups yet."
        # if len(event_pack.body[1]) > 20:
        #     return "Invalid usage of $expiry: provided member UID is too long."
        # member_UID = event_pack.body[1]
        # if member_UID.isalnum() is not True:
        #     return "Invalid usage of $expiry: arguments must not contain non-alphanumeric characters"
