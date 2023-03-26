# from ..command import Command
# from ..eventpackage import EventPackage
# from ..command import CommandCodeResponse as CCR

# import botconfig

# import os, random

# LOCAL = os.path.dirname(os.path.realpath(__file__))

# ALLOWED = []
# ANSWERS = []

# # database keys
# ANSWER = "word"
# HISTORY = "history"
# AVAIL_LETTERS = "aletters"
# POINTS = "points"

# def log(string):
#     print("WORDLE: " + string)

# def list2str(l):
#     s = ""
#     for i in l:
#         s += str(i)
#     return s

# class WordleCommand(Command):
#     def __init__(self):
#         super().__init__()
#         self.name = "$wordle" # this is required in order for the command to run!
        
#         # define what will be shown when someone calls "help $<your command>"
#         self.help = "$wordle | Play wordle!"
        
#         self.author = "spacedog"
#         self.last_updated = "Feb. 7, 2022"

#         global ALLOWED
#         global ANSWERS

#         log("Reading wordle files...")
#         with open(LOCAL + "/static/wordle_allowed.txt", "r") as f:
#             ALLOWED = f.read().split("\n")
#         with open(LOCAL + "/static/wordle_answers.txt", "r") as f:
#             ANSWERS = f.read().split("\n")
#         log("Success!")

#         self.rid = botconfig.ROOM_ID_BOTTOY
#         self.reset()

#     def get_answer(self):
#         a = self.db_get(self.rid + ANSWER)
#         return a.decode() if a is not None else None

#     def get_history(self):
#         h = self.db_list_get(self.rid + HISTORY)
#         return [i.decode() for i in h]

#     def get_history_len(self):
#         return self.db_list_len(self.rid + HISTORY)

#     def get_history_item(self, n):
#         history = self.get_history()
#         return history[n] if (history is not None and len(history) >= (n + 1)) else "-----        "

#     def get_points(self, user):
#         pts = self.db_hash_get(POINTS, user)
#         return int(pts.decode()) if pts is not None else 0

#     def add_points(self, user, points):
#         self.db_hash_incrby(POINTS, user, points)
#         return self.get_points(user)

#     def log_guess(self, word):
#         self.db_rpush(self.rid + HISTORY, word)
#         history = self.get_history()
#         return len(history)

#     def get_avail(self):
#         return self.db_get(self.rid + AVAIL_LETTERS).decode()
    
#     def set_avail(self, avail):
#         self.db_set(self.rid + AVAIL_LETTERS, avail)

#     def reset(self):
#         self.db_set(self.rid + ANSWER, random.choice(ANSWERS))
#         self.db_del(self.rid + HISTORY)
#         self.db_set(self.rid + AVAIL_LETTERS, "q w e r t y u i o p\na s d f g h j k l\n  z x c v b n m")

#         log("picked " + self.get_answer())
    
#     def usage(self):
#         return "Guess words with \"$wordle [guess]\"."

#     def run(self, event_pack: EventPackage):
#         self.rid = event_pack.room_id

#         if self.rid == botconfig.ROOM_ID_GEEKS:
#             return CCR("Only nerds play wordle in #geeks (try #bottoy or a dm).")

#         if self.get_answer() is None:
#             self.reset()
#             log("Reset because of empty game")

#         return self.guess(event_pack)

#     def chart(self):
#         avails = self.get_avail().splitlines()

#         chart  = "1. " + self.get_history_item(0) + "  Letters still available:" + "\n"
#         chart += "2. " + self.get_history_item(1) + "  " + avails[0] + "\n"
#         chart += "3. " + self.get_history_item(2) + "  " + avails[1] + "\n"
#         chart += "4. " + self.get_history_item(3) + "  " + avails[2] + "\n"
#         chart += "5. " + self.get_history_item(4) + "\n"
#         chart += "6. " + self.get_history_item(5) + "\n"
#         return chart

#     def guess(self, event_pack: EventPackage):
#         body = event_pack.body
#         sender = event_pack.sender
#         nick = sender.split(":")[0][1:]

#         # check for legal guess
#         if len(body) < 2:
#             # no guess provided, just print chart with points on top
#             pts = self.get_points(sender)
#             pts_s = nick + ", you have " + str(pts) + " points."
#             return CCR(pts_s + "\n" + self.chart())
        
#         word = body[1].lower()
#         if len(word) != 5:
#             # invalid length
#             return CCR("Guesses have to be 5 letter words.")

#         if word not in ALLOWED and word not in ANSWERS:
#             # invalid word
#             return CCR("That's not a word!")

#         # duplicate words
#         history = self.get_history()
#         # history is stored as the guess plus the info on the end, which we don't
#         # care about here
#         for line in history:
#             old_word = line.split(" ")[0]
#             if word == old_word:
#                 return CCR("\"" + word + "\" was already guessed!")

#         # evaluate guess
#         answer = self.get_answer()
#         guess_number = self.get_history_len() + 1
#         avail = self.get_avail()

#         answerl = list(answer)

#         # check for correctness
#         if word == answer:
#             old_points = self.get_points(sender)
#             new_points = self.add_points(sender, 7 - guess_number)

#             self.reset()
#             return CCR("Correct! The answer was \"" + answer + "\".\n" + nick + " got points for their answer. (" + str(old_points) + " -> " + str(new_points) + ")")
#         elif guess_number == 6:
#             self.reset()
#             return CCR("Incorrect! You're out of guesses. The answer was \"" + answer + "\".")
#         else:
#             info = list(".....")

#             # process greys
#             for i in range(5):
#                 if word[i] not in answer:
#                     avail = avail.replace(word[i], ".")
            
#             # process greens
#             for i in range(5):
#                 if word[i] == answerl[i]:
#                     info[i] = word[i].upper()
#                     answerl[i] = " " # don't double count stuff

#             # process yellows
#             for i in range(5):
#                 if info[i] != word[i].upper() and word[i] in answerl:
#                     info[i] = word[i].lower()
#                     # replace first instance
#                     for j, l in enumerate(answerl):
#                         if l == word[i]:
#                             answerl[j] = " "
#                             break

#             info = "(" + list2str(info) + ")"

#             self.log_guess(word + " " + info)

#             # store avail
#             self.set_avail(avail)

#             return CCR(self.chart())
