### ccawmunity
## computer club community project
HOW TO CONTRIBUTE A FUNCTION

Checklist:

[ ] create a function definition that matches the following

[ ] use the same arguments as others in the same list
    as these are standardized for that event type
    (all COMMANDLIST functions are for message.text events)

[ ] make sure you're returning a string

[ ] add the function chat name to the COMMANDLIST dictionary
    as a key AND the function definition name as the value
    ie "$test": test

[ ] add the function chat name to the HELPLIST dictionary as
    a key AND a string explaining how to use it as the value
    ie "$test": "$test - returns a String yelling at dolphin"

[ ] double check that the dictionaries follow the format
    "key": value, the last k/v in a dictionary has no trailing comma
