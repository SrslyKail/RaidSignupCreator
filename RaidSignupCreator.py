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

def get_raid_name(SERVER_ID:str, API_KEY:str) -> str:

    #Create the URL to get the last raid
    get_url = f"https://raid-helper.dev/api/v3/servers/{SERVER_ID}/events"

    #Get the last session by filtering for the 0th "postedEvents" in the given server
    last_session = requests.get(url=get_url, headers={"Authorization": API_KEY}).json()["postedEvents"][0]

    #Get the title of the last session
    last_session_title = last_session["title"]

    #Split it by [fight_name, date] and keep the fight_name
    next_session_title = last_session_title.split(" - ")[0]

    return next_session_title

def submit_raid_request(next_dateTime:datetime, CHANNEL_ID:str, SERVER_ID:str, API_KEY:str):
    
    #Unix conversion, in case we want to use this later.
    unix = time.mktime(next_dateTime.timetuple())

    #Put together the data we want to post up
    dict = {
        "leaderId": os.getenv('DISCORD_ID'),
        "templateId": 10,
        "date": next_dateTime.strftime("%d-%m-%Y"),
        "time": next_dateTime.strftime("%H:%M"), 
        "title": f"{get_raid_name(SERVER_ID=SERVER_ID, API_KEY=API_KEY)} - {next_dateTime.strftime('%A')}"
    }

    #Get the URL we want to post it to
    POST_URL = f"https://raid-helper.dev/api/v2/servers/{SERVER_ID}/channels/{CHANNEL_ID}/event"

    #Post it
    req = requests.post(url=POST_URL, headers={"Authorization": API_KEY, "Content-Type": "application/json"}, json=dict)

def main():
    load_configuration()
    
    CHANNEL_ID = os.getenv('CHANNEL_ID')
    SERVER_ID = os.getenv('SERVER_ID')
    API_KEY = os.getenv('API_KEY')

    next_date = get_next_date()

    #Submit next raid
    submit_raid_request(next_date, CHANNEL_ID, SERVER_ID, API_KEY)

if __name__=="__main__":
    main()
