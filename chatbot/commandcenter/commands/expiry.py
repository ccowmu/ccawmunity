from ..command import Command
from ..eventpackage import EventPackage

import ldap3
import ssl
import string
from datetime import date
from os import environ

class ExpiryCommand(Command):
    def __init__(self):
        self.name = "$expiry"
        self.help = "$expiry | Gets a member's expiration date from their UID. | Usage: $expiry dolphin"
        self.author = "nothingbutflowers"
        self.last_updated = "Sept. 29, 2018"

    def run(self, event_pack: EventPackage):
        if len(event_pack.body) < 2:
            return "Invalid usage of $expiry: not enough arguments. usage: $expiry dolphin"
        if len(event_pack.body) > 2:
            return "Invalid usage of $expiry: too many arguments. $expiry does not support multiple lookups yet."
        if len(event_pack.body[1]) > 20:
            return "Invalid usage of $expiry: provided member UID is too long."
        member_UID = event_pack.body[1]
        if member_UID.isalnum() is not True:
            return "Invalid usage of $expiry: arguments must not contain non-alphanumeric characters"
        
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
        
        try:
            preparedQuery = "(uid=" + member_UID + ")"
            conn.search(search_base=MEMBER_BASE,
                        search_filter=preparedQuery, attributes=DESIRED_FIELDS)
            result = conn.entries[0]
            unix_timestamp = result["shadowExpire"].value * POSIX_DAY
            return str(date.fromtimestamp(unix_timestamp).strftime('%Y-%m-%d'))
        except Exception as e:
            print("something went wrong:", e)
            return "this error message is incredibly helpful!"
        finally:
            conn.unbind()
