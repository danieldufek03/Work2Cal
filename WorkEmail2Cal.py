'''
This program is designed to sift through my emails for my work shcedule, then add
shifts as events in my google calendar. 
'''
import httplib2
import os
from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools
from datetime import datetime, timedelta
import Gmail_Client

login = raw_input("Input login name\n")
password = raw_input("Input password\n")

clientObject = Gmail_Client.Gmail_Client(login, password) #connects to the given gmail account
#Selects the shift line from firebrew schedule emails
shifts = clientObject.parse('(FROM "Schedulefly" SUBJECT "Schedule")', r'(\w+\w+\w+ \d+/\d+ \d+:\d+\d+\w+\w)')


#list to store datetimes for putting in google calendar
shiftList = []

now = datetime.now()
#turns shifts found in email into dateTime objects and stores them in shiftList
for result in shifts:
    shift = result.group()
    date_object = datetime.strptime(shift, "%a %m/%d %I:%M%p") #convert shifts to datetimes
    cal_date = date_object.replace(year = now.year)
    shiftList.append(cal_date)
    
print(shiftList)


#Google told me to put this here
try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def main():
    """Shows basic usage of the Google Calendar API.

    Creates a Google Calendar API service object and outputs a list of the next
    10 events on the user's calendar.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    for work in shiftList:
        workBegin = work.isoformat()
        workEnd = work + timedelta(hours=5)
        workEnd = workEnd.isoformat()
        event = {
          'summary': 'Firebrew Shift',
          'location': '1253 Nimmo Pkwy, Virginia Beach, VA 23456, United States',
          'description': 'Work',
          'start': {
            'dateTime': workBegin,
            'timeZone': 'America/New_York',
          },
          'end': {
            'dateTime': workEnd,
            'timeZone': 'America/New_York',
          },
          'reminders': {
            'useDefault': False,
            'overrides': [
              {'method': 'email', 'minutes': 24 * 60},
              {'method': 'popup', 'minutes': 10},
            ],
          },
        }

        event = service.events().insert(calendarId='primary', body=event).execute()
        print 'Event created: %s' % (event.get('htmlLink'))


if __name__ == '__main__':
    main()
