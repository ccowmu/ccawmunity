# this file serves as a quick reference for the structure of a custom command class.

# import the Command parent class, and the EventPackage class.
from ..command import Command
from ..eventpackage import EventPackage
import requests
from bs4 import BeautifulSoup

BASE_URL = 'https://wmich.edu/classlookup/wskctlg.wskctlg_menu'
ARG_LIST = ['-n', '-c', '-t', '-s']

class ClassSection():
    def __init__(self, crn: str, section: str, date: str, day: str, time: str, insm: str, loc: str, instructor: str, credit: str, is_lab: bool = False) -> None:
        self.crn = crn
        self.section = section
        self.date = date
        self.day = day
        self.time = time
        self.insm = insm
        self.loc = loc
        self.instructor = instructor
        self.credit = credit
        self.is_lab = is_lab
    
    def __str__(self):
        return 'CRN: ' + str(self.crn) + 'SECTION: ' + str(self.section)
    
    def __repr__(self) -> str:
        return 'CRN: ' + str(self.crn) + 'SECTION: ' + str(self.section)


# create a class that inherits from Command
class CourseLookupCommand(Command):
    # set the name and author of the command inside of its constructor.
    def __init__(self):
        super().__init__() # this is necessary in order to initialize optional attributes with default values

        self.name = "$courselookup" # this is required in order for the command to run!
        
        # define what will be shown when someone calls "help $<your command>"
        self.help = "$courselookup | Pull info on courses from WMU course catalog."
        
        self.author = "acp"
        self.last_updated = "Mar 26, 2023"
        self.aliases = ["lookup", "clookup", "course"]

    # define what the command does here.
    # this function must return a string. the string will be sent to the room.
    def run(self, event_pack: EventPackage):
        args = self.parse_args(event_pack)
        form_data = {'ctrl':'catalog',
                     'lownum':'1',
                     'collapse': 'N',
                     'lines': '50',
                     'term': '202340',
                     'campus': '',
                     'crse': '',
                     'mtypCode': '',
                     'insm': '',
                     'instr': '',
                     'attr': '',
                     'subject': ''
                     }

        form_data['crse'] = args['-c']
        form_data['term'] = args['-t']
        form_data['subject'] = args['-s']


        html = requests.post(BASE_URL, data=form_data).text
        soup = BeautifulSoup(html, 'html.parser')
        crns = soup.find_all('td', {'class': 'crn_td'})
        sections = soup.find_all('td', {'class': 'section_td'})
        dates = soup.find_all('td', {'class': 'date'})
        days = soup.find_all('td', {'class': 'days'})
        times = soup.find_all('td', {'class': 'time'})
        insms = soup.find_all('td', {'class': 'insm'})
        locs = soup.find_all('td', {'class': 'loc'})
        instructors = soup.find_all('td', {'class': 'instr_td'})
        credits = soup.find_all('td', {'class': 'crhr_td'})
        seats = soup.find_all('table', {'class': 'avail_seats'})
        courses = []
        for i in range(len(crns) - 1):
            crn = crns[i].findChild('td').text
            section = sections[i].text
            date = dates[i].text
            day = days[i].text
            insm = insms[i].text
            time = times[i].text
            loc = locs[i].text
            instructor = instructors[i].text
            credit = credits[i].text
            # seat
            courses.append(ClassSection(crn, section, date, day, insm, time, loc, instructor, credit))
        out = ''
        if(len(courses) == 0):
            return "No Courses Found"
        for course in courses:
            out += str(course) + '\n'
        return out


    def parse_args(self, event_pack) -> dict:
        arg_dict: dict = {}
        # Default arguments
        arg_dict['-h'] = False
        arg_dict['-v'] = False
        arg_dict['-t'] = 202340
        arg_dict['-s'] = 'CS'
        arg_dict['-c'] = ''
        

        # Iterate through args and fill arg_dict
        for i in range(len(event_pack.body)):
            if(i == 0):
                continue
            elif(event_pack.body[i] == '-h'):
                arg_dict['-h'] = True
            elif(event_pack.body[i] == '-v'):
                arg_dict['-v'] = True
            elif(event_pack.body[i] in ARG_LIST and type(event_pack.body[i+1] == type(1))):
                arg_dict[event_pack.body[i]] = event_pack.body[i + 1]
        return arg_dict