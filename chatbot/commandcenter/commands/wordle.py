from ..command import Command
from ..eventpackage import EventPackage
from ..command import CommandCodeResponse as CCR

import os, random

LOCAL = os.path.dirname(os.path.realpath(__file__))

ALLOWED = []
ANSWERS = []

# database keys
ANSWER = "word"
HISTORY = "history"
AVAIL_LETTERS = "aletters"
POINTS = "points"

def log(string):
    print("WORDLE: " + string)

def list2str(l):
    s = ""
    for i in l:
        s += i
    return s

class WordleCommand(Command):
    def __init__(self):
        self.name = "$wordle" # this is required in order for the command to run!
        
        # define what will be shown when someone calls "help $<your command>"
        self.help = "$wordle | Play wordle!"
        
        self.author = "spacedog"
        self.last_updated = "Feb. 6, 2022"

        global ALLOWED
        global ANSWERS

        log("Reading wordle files...")
        with open(LOCAL + "/static/wordle_allowed.txt", "r") as f:
            ALLOWED = f.read().split("\n")
        with open(LOCAL + "/static/wordle_answers.txt", "r") as f:
            ANSWERS = f.read().split("\n")
        log("Success!")

        self.reset()

    def get_answer(self):
        return self.db_get(ANSWER).decode()

    def get_history(self):
        return self.db_list_get(HISTORY)

    def get_history_len(self):
        return self.db_list_len(HISTORY)

    def get_history_item(self, n):
        history = self.get_history()
        return history[n].decode() if (history is not None and len(history) >= (n + 1)) else "-----"

    def get_points(self, user):
        pts = self.db_hash_get(POINTS, user)
        return int(pts.decode()) if pts is not None else 0

    def add_points(self, user, points):
        self.db_hash_incrby(POINTS, user, points)
        return self.get_points(user)

    def log_guess(self, word):
        self.db_rpush(HISTORY, word)
        history = self.get_history()
        return len(history)

    def get_avail(self):
        return self.db_get(AVAIL_LETTERS).decode()

    def reset(self):
        self.db_set(ANSWER, random.choice(ANSWERS))
        self.db_del(HISTORY)
        self.db_set(AVAIL_LETTERS, "qwertyuiop\nasdfghjkl\nzxcvbnm")

        log("picked " + self.get_answer())
    
    def usage(self):
        return "Guess words with \"$wordle [guess]\"."

    def run(self, event_pack: EventPackage):
        if self.get_answer != "":
            # in-progress game
            return self.guess(event_pack)
        else:
            # restart game
            # in theory this should never happen
            self.reset()
            return CCR("Game started. " + self.usage()) 

    def chart(self):
        chart  = "1. " + self.get_history_item(0) + "\n"
        chart += "2. " + self.get_history_item(1) + "\n"
        chart += "3. " + self.get_history_item(2) + "\n"
        chart += "4. " + self.get_history_item(3) + "\n"
        chart += "5. " + self.get_history_item(4) + "\n"
        chart += "6. " + self.get_history_item(5) + "\n"
        chart += "\n"
        chart += "Letters still available:\n"
        chart += self.get_avail()
        return chart

    def guess(self, event_pack: EventPackage):
        body = event_pack.body
        sender = event_pack.sender
        nick = sender.split(":")[0][1:]

        # check for legal guess
        if len(body) < 2:
            # no guess provided, just print chart with points on top
            pts = self.get_points(sender)
            pts_s = nick + ", you have " + str(pts) + " points."
            return CCR(pts_s + "\n" + self.chart())
        
        word = body[1].lower()
        if len(word) != 5:
            # invalid length
            return CCR("Guesses have to be 5 letter words.")

        if word not in ALLOWED and word not in ANSWERS:
            # invalid word
            return CCR("That's not a word!")

        # evaluate guess
        answer = self.get_answer()
        guess_number = self.get_history_len() + 1
        avail = self.get_avail()

        answerl = list(answer)

        # check for correctness
        if word == answer:
            old_points = self.get_points(sender)
            new_points = self.add_points(sender, 7 - guess_number)

            self.reset()
            return CCR("Correct! The answer was \"" + answer + "\".\n" + nick + " got points for their answer. (" + str(old_points) + " -> " + str(new_points) + ")")
        elif guess_number == 6:
            self.reset()
            return CCR("Incorrect! You're out of guesses. The answer was \"" + answer + "\".")
        else:
            info = "("
            for i in range(5):
                if word[i] == answerl[i]:
                    # "green"
                    info += word[i].upper()
                elif word[i] in answerl:
                    # "yellow"
                    info += word[i].lower()
                    answerl[i] = " " # don't double count stuff
                else:
                    # "grey"
                    info += "."
                    avail = avail.replace(word[i], ".")
            
            info += ")"
            self.log_guess(word + " " + info)

            # store avail
            self.db_set(AVAIL_LETTERS, avail)

            return CCR(self.chart())
