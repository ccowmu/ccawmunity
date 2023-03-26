# this file serves as a quick reference for the structure of a custom command class.

# import the Command parent class, and the EventPackage class.
from ..command import Command
from ..eventpackage import EventPackage
import requests
from bs4 import BeautifulSoup

BASE_URL = 'https://wmich.edu/classlookup/wskctlg.wskctlg_menu'

class ClassSection():
    def __init__(self, crn: int, section, date, day, time, insm, loc, instructor, credit) -> None:
        self.crn = crn
        self.section = section
        self.date = date
        self.day = day
        self.time = time
        self.insm = insm
        self.loc = loc
        self.instructor = instructor
        self.credit = credit

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
                     'subject': 'ADA'
                     }
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
        for i in range(len(crns)):
            crn = crns[i].findChild('td').text
            section = sections[i].findChild('td').text
            date = dates[i].findChild('td').text
            day = days[i].findChild('td').text
            time = times[i].findChild('td').text
            insm = insms[i].findChild('td').text
            loc = locs[i].findChild('td').text
            instructor = instructors[i].findChild('td').text
            credit = credits[i].findChild('td').text
            # seat
            courses.append(ClassSection(crn))
        return courses[0].crn
