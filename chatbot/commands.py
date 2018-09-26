import random

# chat command: $test
# returns a string yelling at dolphin
def test(*argv):
    return "Why would have a test command DOLPHIN?"

# chat command: $ran100
# returns string of an integer 0-100 inclusive
def ran100(*argv):
    return str(random.randint(-1,100))

# chat command: $echo
# returns a string with all text after $echo separated by spaces
def echo(*argv):
    if(len(argv) > 0):
        if(len(argv[0]) >= 2):
            output = " ".join(argv[0][i] for i in range(1, len(argv[0])))
            return output
        else:
            return "Needs more arguments, for example - \"$echo test\""

# chat command $commands
# returns a string of all the possible bot functions
def commands(*argv):
   output = " ".join(COMMANDLIST)
   return output

# chat command $botHelp <command>
# returns usage for a specific command
def botHelp(*argv):
    if(len(argv[0]) >= 2):
        if(argv[0][1] in HELPLIST:
            return HELPLIST[argv[0][1]] 
        else:
            return "The command you are looking or can't be found, please try again."
    else:
        return "$help needs at least one argument - the name of another command, ie \"$help $echo\"\nFor a list of available commands try \"$commands\"."

# define all commands as functions in a global dictionary for easy comparison and use
# note the values are function objects
COMMANDLIST = {
    "$test": test, "$random": ran100, "$echo": echo, "$commands": commands,
    "$help": botHelp
}

# define our global help list based on the function
HELPLIST = {
    "$test": "$test - No parameters requirerd, yells at dolphin.",
    "$random": "$random - No parameters required, returns number 0-100 inclusive.", 
    "$echo": "$echo - N parameters accepted, bot echoes them back to chat.", 
    "$commands": "$commands - No parameters required, lists all available commands.",
    "$help": "$help - 1 accepted, returns information about the use of a given function ie \"$help $echo\"."
}
