# CCAWMUNITY
## Computer Club Community project

# How to create a new command

To create a new command:
1. Clone this repository.
2. Create a new branch for your command with `git checkout -b <name of your new branch>`
3. Create a python file called `<your new command>.py` in the `commands` directory.
4. Inside the new python file, create a custom command class that inherits from the `Command` parent class in the `command` module. See [the template file](./commands/template.py) if you want to see an example. Check `./commands/README.md` for more details on what your command class should look like.
5. When you're done, submit a pull request to this repo. Be sure to include what your command does within the pull request information.
