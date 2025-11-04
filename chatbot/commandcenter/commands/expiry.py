from ..command import Command
from ..command import CommandCodeResponse
from ..eventpackage import EventPackage

import ldap3
import string
import time
from datetime import date
from os import environ

class ExpiryCommand(Command):
    def __init__(self):
        super().__init__()
        self.name = "$expiry"
        self.help = "$expiry | Gets a member's expiration date from their UID. | Usage: $expiry dolphin"
        self.author = "nothingbutflowers, sphinx"
        self.last_updated = "Nov. 4, 2025"
        self.whitelist = ["crosstangent", "kahrl", "sphinx", "rezenee", "estlin"]

    def run(self, event_pack: EventPackage):
        LDAP_URL = 'ldap://openldap:389'
        MEMBER_BASE = 'cn=members,dc=yakko,dc=cs,dc=wmich,dc=edu'
        POSIX_DAY = 86400
        DESIRED_FIELDS = ["shadowExpire"]
        
        server = ldap3.Server(LDAP_URL)
        conn = ldap3.Connection(
            server, 
            user="cn=readonly,dc=yakko,dc=cs,dc=wmich,dc=edu", 
            password=environ.get("LDAP_PASSWORD", ""), 
            auto_bind=True
        )

        args = event_pack.body[1:]
        nick = event_pack.sender.split(":")[0][1:]

        try:
            if len(args) == 0:
                # no args given, assume sender wants own expiry
                preparedQuery = "(uid=" + nick + ")"
                conn.search(search_base=MEMBER_BASE,
                            search_filter=preparedQuery, attributes=DESIRED_FIELDS)
                
                if not conn.entries:
                    return "I don't know who {} is!".format(nick)
                
                result = conn.entries[0]
                if result["shadowExpire"].value == None:
                    # user doesn't expire
                    return "{} doesn't expire!".format(nick)
                
                unix_timestamp = result["shadowExpire"].value * POSIX_DAY
                return "{}: {}".format(nick, str(date.fromtimestamp(unix_timestamp).strftime('%Y-%m-%d')))
                
            elif args[0] == "-a":
                # Check all expired members
                if nick not in self.whitelist:
                    return "You don't have permission to use this command."
                
                preparedQuery = "(shadowExpire<=" + str(int(time.time()) // 86400) + ")"
                conn.search(search_base=MEMBER_BASE,
                            search_filter=preparedQuery, attributes=["uid", "shadowExpire"])
                
                if not conn.entries:
                    return "No expired members found."
                
                expiries = []
                for e in conn.entries:
                    unix_timestamp = e["shadowExpire"].value * POSIX_DAY
                    str_timestamp = str(date.fromtimestamp(unix_timestamp).strftime('%Y-%m-%d'))
                    expiries.append((e["uid"].value, str_timestamp))
                
                expiries = sorted(expiries, key=lambda x: x[0])
                
                result = ""
                for e in expiries:
                    result += "{}: {}\n".format(e[0], e[1])
                return CommandCodeResponse(result)
            
            else:
                # Lookup specific user
                preparedQuery = "(uid=" + args[0] + ")"
                conn.search(search_base=MEMBER_BASE,
                            search_filter=preparedQuery, attributes=DESIRED_FIELDS)
                
                if not conn.entries:
                    return "I don't know who {} is!".format(args[0])
                
                result = conn.entries[0]
                if result["shadowExpire"].value == None:
                    # user doesn't expire
                    return "{} doesn't expire!".format(args[0])
                
                unix_timestamp = result["shadowExpire"].value * POSIX_DAY
                return "{}: {}".format(args[0], str(date.fromtimestamp(unix_timestamp).strftime('%Y-%m-%d')))
                
        except ldap3.core.exceptions.LDAPException as e:
            print("LDAP error:", e)
            return "Failed to query LDAP server."
        except Exception as e:
            print("Unexpected error:", e)
            return "An error occurred while processing your request."
        finally:
            if conn.bound:
                conn.unbind()