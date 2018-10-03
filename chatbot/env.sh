#!/bin/bash
#this file is intended to be used for sensitive variables only
#ensure you do not push this file to the repo.
#all non-sensitive variables should be defined in botconfig.py


: <<'END' #begin bash comment

example proper env variable form:
export MY_ENV_VARIABLE="THIS-IS-A-VALUE"

example usage of env.sh:
`source env.sh`

example use via python:
from os import environ
if "MY_ENV_VARIABLE" in environ:
    print(environ["MY_ENV_VARIABLE"])
else:
    print("environment variable has not been set")

END #end bash comment


export BOT_PASSWORD=

#export LDAP_URL=
#export LDAP_MEMBER_BASE=
#export LDAP_READONLY_DN=
#export LDAP_READONLY_PASSWORD=
