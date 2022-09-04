# this file serves as a quick reference for the structure of a custom command class.

# import the Command parent class, and the EventPackage class.
from ..command import Command
from ..eventpackage import EventPackage
import random

class TemplateCommand(Command):
    
    def __init__(self):
        super().__init__() 

        self.name = "$knockers" # enter this to see ascii titties
        self.aliases = ["$boobs", "$bosom", "$breasts", "$cleavage", "$hooters", "$melons", "$pairs", "$titties", "udders"]

        self.help = "$knockers | Shows ascii titties :D"
        
        self.author = "Chago"
        self.last_updated = "Sept 3, 2022"

    
    def run(self, event_pack: EventPackage):

        # list of titties
        tittyList = ["(o)(o)", "( + )( + )", "(*)(*)", "(@)(@)", "oo", "{ O }{ O }", "(oYo)",
                        "( ^ )( ^ )", "(o)(O)", "(Q)(Q)", "(p)(p)", "(  -  )(  -  )", "|o||o|", "($)($)",
                        "（。ㅅ 。）", "(•_ㅅ_•)", "(@ㅅ@)", ":-)B", "༼༼+༽༽༼༼+༽༽", "(. | .)", "( • ) ( • )", 
                        "(   +   )   (   +   )", "( • )( • )ԅ(≖‿≖ԅ)", "(* )( *)", "(  ・  ) | ( ・  )", 
                        "(◟‿◞◟‿◞)", "༼*༽༼*༽", "(  .)(.  )"]

        # TODO: reeturn a random element of titty list lololol  
        return random.choice(tittyList)
