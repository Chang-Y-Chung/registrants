
import requests
import datetime

class Princetonian:

    url = 'http://search.princeton.edu/vcard/index/netid/{0}'

    def __init__(self, netid):
        self.netid = netid
        r = requests.get(Princetonian.url.format(netid))
        if r.status_code != 200: return

        self.updated = str(datetime.datetime.now()).split('.')[0]
        self.status = 'student'

        for line in r.content.split('\n'):
            if line.startswith('N:'):
                names = line.split(':')[1].split(';')
                self.firstname = names[1].strip()
                self.lastname = names[0].strip()
            elif line.startswith('ORG:'):
                self.department = line.split(':')[1].strip();
            elif line.startswith('TITLE:'):
                self.status = 'faculty/staff';
            elif (line.startswith('EMAIL;') and 'type=PREF' in line):
                self.email = line.split(':')[1].strip();

    def __str__(self):
        sb = ['{0}: "{1}"'.format(k, v) for k, v in self.__dict__.items()]
        return '{ ' + ', '.join(sb) + '}'

    def __repr__(self):
        return self.__str__()

if __name__ == '__main__':
    faculty = Princetonian('mjs3')
    staff = Princetonian('cchung')
    student = Princetonian('dfeehan')
    print faculty
    print staff
    print student

