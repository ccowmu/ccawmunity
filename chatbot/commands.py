import random
import ldap3
import ssl
from datetime import datetime
from os import environ

# HOW TO CONTRIBUTE A FUNCTION
#
# Checklist:
#
# [ ] create a function definition that matches the following
#
# [ ] use the same arguments as others in the same list
#     as these are standardized for that event type
#     (all COMMANDLIST functions are for message.text events)
#
# [ ] make sure you're returning a string
#
# [ ] add the function chat name to the COMMANDLIST dictionary
#     as a key AND the function definition name as the value
#     ie "$test": test
#
# [ ] add the function chat name to the HELPLIST dictionary as
#     a key AND a string explaining how to use it as the value
#     ie "$test": "$test - returns a String yelling at dolphin"
# 
# [ ] double check that the dictionaries follow the format
#     "key": value, the last k/v in a dictionary has no trailing comma

# chat command: $test
# returns String - yelling at dolphin
def test(body={}, roomId="", sender="", event={}):
    return "Why would have a test command DOLPHIN?"

# chat command: $ran100
# returns String - of an integer 0-100 inclusive
def ran100(body={}, roomId="", sender="", event={}):
    return str(random.randint(-1,100))

# chat command: $echo
# returns String - with all text after $echo separated by spaces
def echo(body={}, roomId="", sender="", event={}):
    if(len(body) >= 2):
        output = " ".join(body[i] for i in range(1, len(body)))
        return output
    else:
        return "Needs more arguments, for example - \"$echo test\""

# chat command $commands
# returns String - of all the possible bot functions
def commands(body={}, roomId="", sender="", event={}):
   output = " ".join(COMMANDLIST)
   return output

# chat command $botHelp <command>
# returns String - usage for a specific command
def botHelp(body={}, roomId="", sender="", event={}):
    if(len(body) >= 2):
        if(body[1] in HELPLIST):
            return HELPLIST[body[1]] 
        else:
            return "The command you are looking or can't be found, please try again."
    else:
        return("$help needs at least one argument - the name of another command, ie \"$help $echo\"" \
                "\nFor a list of available commands try \"$commands\".")

# chat command $eccho
# returns String - a e s t h e t i c echo
def eccho(body={}, roomId="", sender="", event={}):
    return "e c h o"

# chat command $contribute
# returns a String - url for the repository
def contribute(body={}, roomId="", sender="", event={}):
    return "Contribute a function! https://github.com/ccowmu/ccawmunity"

# chat command $expiry
# takes one uid
# returns a String - user expiration date
def expiry(body={}, roomId="", sender="", event={}):
    LDAP_URI = "ldap://cclub.cs.wmich.edu:389"
    MEMBER_BASE = 'cn=members,dc=yakko,dc=cs,dc=wmich,dc=edu'
    POSIX_DAY = 86400
    DESIRED_FIELDS = ["shadowExpire"]

    tls_config = ldap3.Tls(validate=ssl.CERT_REQUIRED)
    server = ldap3.Server(LDAP_URI, use_ssl=True, tls=tls_config)
    conn = ldap3.Connection(server, user="cn=readonly,dc=yakko,dc=cs,dc=wmich,dc=edu", password=environ.get("LDAP_READONLY_PASSWORD"), auto_bind="NONE", read_only=True)
    
    conn.open()
    conn.start_tls()
    conn.bind()

    try:
        preparedQuery = "(uid="+ str(body[1]) + ")"
        r = conn.search(search_base=MEMBER_BASE, search_filter=preparedQuery, attributes=DESIRED_FIELDS)
        res = conn.entries[0]
        shadow_expire = res["shadowExpire"].value
        unix_timestamp = shadow_expire * POSIX_DAY
        return str(datetime.utcfromtimestamp(unix_timestamp).strftime('%Y-%m-%d'))
    except:
        return "something went wrong"
    finally:
        conn.unbind()

# REMINDER - make sure the commas follow every k/v pair except
#            for the last one in each dictionary!

# define all commands as functions in a global dictionary for easy comparison and use
# note the values are function objects
COMMANDLIST = {
    "$test": test, "$random": ran100, "$echo": echo, "$commands": commands,
    "$help": botHelp, "$eccho": eccho, "$contribute": contribute, "$expiry": expiry
}

# define our global help list based on the function
HELPLIST = {
    "$test": "$test - No parameters requirerd, yells at dolphin.",
    "$random": "$random - No parameters required, returns number 0-100 inclusive.", 
    "$echo": "$echo - N parameters accepted separated by spaces, bot echoes them back to chat.\"$echo arg1 arg2\"", 
    "$commands": "$commands - No parameters required, lists all available commands.",
    "$help": "$help - 1 accepted, returns information about the use of a given function ie \"$help $echo\".",
    "$eccho": "$eccho - No parameters required, inside A E S T H E T I C joke.",
    "$contribute": "$contribute - No parameters required, links the repository url.",
    "$expiry": "$expiry - takes one uid, returns expiry date for user"
}