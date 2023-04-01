# this file serves as a quick reference for the structure of a custom command class.

# import the Command parent class, and the EventPackage class.
from ..command import Command
from ..command import CommandCodeResponse
from ..eventpackage import EventPackage
import requests
from datetime import datetime
from bs4 import BeautifulSoup

BASE_URL = 'https://wmich.edu/classlookup/wskctlg.wskctlg_menu'
ARG_LIST = ['-n', '-c', '-t', '-s', '-h']
HELP_TEXT = ''' $courselookup | Pull information from WMU Course Catalog
Usage: $courselookup <args>
Arguments:
-c: Course number.
-t: Semester, defaults to current semester.
-s: Subject, defaults to CS.
-h: Print help text.
'''

class ClassSection():
    def __init__(self, crn: str, section: str, crse_num, crse_name, date: str, day: str, time: str, insm: str, loc: str, instructor: str, credit: str, is_lab: bool = False) -> None:
        self.crn = crn
        self.section = section
        self.crse_num = crse_num
        self.crse_name = crse_name
        self.date = date
        self.day = day
        self.time = time
        self.insm = insm
        self.loc = loc
        self.instructor = instructor
        self.credit = credit
        self.is_lab = is_lab
    
    def __str__(self):
        out = self.crse_num + ' ' + self.crse_name
        if(self.is_lab):
           out += ' Lab'
        out += ' ' + 'CRN: ' + str(self.crn) + ' ' + 'SECTION: ' + str(self.section) + ' INSTRUCTOR: ' + str(self.instructor)
        return out
    
    def __repr__(self) -> str:
        return 'CRN: ' + str(self.crn) + 'SECTION: ' + str(self.section)


# create a class that inherits from Command
class CourseLookupCommand(Command):
    # set the name and author of the command inside of its constructor.
    def __init__(self):
        super().__init__() # this is necessary in order to initialize optional attributes with default values

        self.name = "$courselookup" # this is required in order for the command to run!
        
        # define what will be shown when someone calls "help $<your command>"
        self.help = "$courselookup | Pull info on courses from WMU course catalog. Please use -h for more details"
        
        self.author = "acp"
        self.last_updated = "Mar 26, 2023"
        self.aliases = ["$lookup", "$clookup", "$course"]

    # define what the command does here.
    # this function must return a string. the string will be sent to the room.
    def run(self, event_pack: EventPackage):
        args = self.parse_args(event_pack)
        if(args['-h']):
            return HELP_TEXT
        form_data = {'ctrl':'catalog',
                     'lownum':'1',
                     'collapse': 'N',
                     'lines': '20',
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
        crses = soup.find_all('td', {'class': 'crselink'})
        dates = soup.find_all('td', {'class': 'date'})
        days = soup.find_all('td', {'class': 'days'})
        times = soup.find_all('td', {'class': 'time'})
        insms = soup.find_all('td', {'class': 'insm'})
        locs = soup.find_all('td', {'class': 'loc'})
        instructors = soup.find_all('td', {'class': 'instr_td'})
        credits = soup.find_all('td', {'class': 'crhr_td'})
        seats = soup.find_all('table', {'class': 'avail_seats'})
        courses = []
        for i in range(len(crns)):
            crn = crns[i].findChild('td').text
            lab_object = crns[i].find('td', {'class': 'linked_crse'})
            lab_text = ''
            if(lab_object):
                lab_text = lab_object.text
            lab_bool = False
            if(lab_text == 'Lab'):
                lab_bool = True
            section = sections[i].text
            crse = crses[i].findChild('a').get_text(separator='</b>').split('</b>')
            crse_num = crse[0]
            crse_name = crse[1]
            date = dates[i].text
            day = days[i].text
            insm = insms[i].text
            time = times[i].text
            loc = locs[i].text
            instructor = instructors[i].get_text(separator='</b>').split('</b>')[0]
            credit = credits[i].text
            courses.append(ClassSection(crn, section, crse_num, crse_name, date, day, insm, time, loc, instructor, credit, lab_bool))
        out = 'The following are the first 20 courses that fit your query\n'
        if(len(courses) == 0):
            return "No Courses Found"
        for course in courses:
            out += str(course) + '\n'
        return CommandCodeResponse(out)


    def parse_args(self, event_pack) -> dict:
        arg_dict: dict = {}
        # Default arguments
        arg_dict['-h'] = False
        arg_dict['-v'] = False
        arg_dict['-t'] = self.find_date()
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
    
    def find_date(self):
        now = datetime.now()
        sem = 0
        if(8 <= now.month <= 12):
            sem = 40
        if(1 <= now.month <= 4):
            sem = 10
        year = datetime.now().year
        return str(year) + str(sem) 
