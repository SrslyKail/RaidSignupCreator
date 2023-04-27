#cSpell:disable
#Default packages installed with python
import time
import os
from datetime import datetime, timedelta

from importlib.util import find_spec
#Check for required additional packages
if find_spec("requests") == None:
    import sys, subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', "requests"])
    del sys, subprocess

if find_spec("dotenv") == None:
    import sys, subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', "python-dotenv"])
    del sys, subprocess

del find_spec

#Then import them
import requests
from dotenv import load_dotenv

#User must supply the following environment variables:
#API_KEY
#SERVER_ID
#CHANNEL_ID
#DISCORD_ID

required_env_variables = ["API_KEY", "SERVER_ID", "CHANNEL_ID"]
def load_configuration():
    load_dotenv()

def get_post_event_url(SERVER_ID:str, CHANNEL_ID:str):
    return f"https://raid-helper.dev/api/v2/servers/{SERVER_ID}/channels/{CHANNEL_ID}/event"

def get_events_info_url(SERVER_ID:str):
    return f"https://raid-helper.dev/api/v3/servers/{SERVER_ID}/events"
    

def get_next_date():
    """
    Returns the date of the next occurrence of a weekday.

    Args:
        today (datetime): Today - must be a datetime object
        
    Return (datetime.date): The date of the the next occurrence of that weekday
    """
    today = datetime.now()

    #If today is wednesday -> Friday
    if 2 <= today.weekday() <= 4:
        #Set next raid day to Saturday
        weekday = 5
    else:
        #Set next raid day to Wednesday
        weekday = 2

    #See how many days ahead we need to go for the next instance of the weekday
    days_delta = weekday - today.weekday()
    #If we already passed that date, or its today
    if days_delta <= 0:
    #we need to add 1 week
        days_delta += 7

    next_date = today + timedelta(days_delta)
    
    #next we need to get the day of week to set the time
    if next_date.weekday() == 2:
        next_date = next_date.replace(hour=18, minute=30)

    elif next_date.weekday() == 5:
        next_date = next_date.replace(hour=12, minute=00)
    else:
        #I can't imagine ever raising this, but might as well in case of errors
        raise Exception("Input date was not a raid day!")
    
    #Clean the seconds/microseconds
    next_date = next_date.replace(second=0, microsecond=0)
    return next_date

def get_posted_session_data(SERVER_ID:str, API_KEY:str) -> dict:
    events_url = get_events_info_url(SERVER_ID)
    sessions_info = dict(requests.get(url=events_url, headers={"Authorization": API_KEY}).json())["postedEvents"]
    return sessions_info

def check_raid_day_availability(next_date: datetime, sessions_info: dict):

    next_session = next_date.date()

    #If the date of the session is after the next_date, break
    for session in sessions_info:
        unix_session_time = session["startTime"]
        session_dateTime=datetime.fromtimestamp(unix_session_time).date()

        #If the next session is before the one we want to make
        if session_dateTime < next_session:
            #We're clear to make a new one
            return True
        elif session_dateTime > next_session:
            #If its after the one we wanna make, keep checking
            continue
        elif session_dateTime == next_session:
            #If its the same, we dont want to make a new one
            return False
        else:
            continue

def get_raid_name(all_sessions_info:dict) -> str:

     #Get the last session by filtering for the 0th "postedEvents" in the given server
    last_posted_event = all_sessions_info[0]

    #Get the title of the last session
    last_session_title = last_posted_event["title"]

    #Split it by [fight_name, date] and keep the fight_name
    next_session_title = last_session_title.split(" - ")[0]
    
    return next_session_title

def submit_raid_request(next_dateTime:datetime, sessions_info:dict, CHANNEL_ID:str, SERVER_ID:str, API_KEY:str):
    
    #Unix conversion, in case we want to use this later.
    unix = time.mktime(next_dateTime.timetuple())

    #Put together the data we want to post up
    dict = {
        "leaderId": os.getenv('DISCORD_ID'),
        "templateId": 10,
        "date": next_dateTime.strftime("%d-%m-%Y"),
        "time": next_dateTime.strftime("%H:%M"), 
        "title": f"{get_raid_name(sessions_info)} - {next_dateTime.strftime('%A')}"
    }

    #Get the URL we want to post it to
    POST_URL = get_post_event_url(SERVER_ID, CHANNEL_ID)

    #Post it
    req = requests.post(url=POST_URL, headers={"Authorization": API_KEY, "Content-Type": "application/json"}, json=dict)

def main():
    load_configuration()
    
    CHANNEL_ID = os.getenv('CHANNEL_ID')
    SERVER_ID = os.getenv('SERVER_ID')
    API_KEY = os.getenv('API_KEY')


    next_date = get_next_date()

    posted_session_data = get_posted_session_data(SERVER_ID, API_KEY)

    if check_raid_day_availability(next_date, posted_session_data) == True:
        #Submit next raid
        submit_raid_request(next_date, posted_session_data, CHANNEL_ID, SERVER_ID, API_KEY)
    else:
        print(f"Event already exists on {next_date.strftime('%d-%m-%Y')}")

if __name__=="__main__":
    main()
