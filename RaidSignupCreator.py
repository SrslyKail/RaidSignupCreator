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
    #Check the required environment variables were created
    envVars = os.environ
    for requiredVar in required_env_variables:
        if requiredVar not in envVars:
            raise Exception(f".env file did not contain {requiredVar}")
        
            

def next_date(today: datetime, weekday:int ):
    """
    Returns the date of the next occurrence of a weekday.

    Args:
        today (datetime): Today - must be a datetime object
        weekday (int): The day of week you want. 0 = Monday, 1 = Tuesday, etc.
        
    Return (datetime.date): The date of the the next occurrence of that weekday
    """
    days_ahead = weekday - today.weekday()
    if days_ahead <= 0: #This means the day of week is today, so we should return 1 week from now
        days_ahead += 7
    return today + timedelta(days_ahead)

def submit_raid_request(fight:str, dateTime:datetime, URL:str, APIKEY:str):
    #First, convert the dateTime to just date.
    date = dateTime.date()
    
    #next we need to get the day of week to set the time
    if dateTime.weekday() == 2:
        dateTime = dateTime.replace(hour=18, minute=30)
    elif date.weekday() == 5:
        dateTime = dateTime.replace(hour=12, minute=00)
    else:
        raise Exception("Input date was not a raid day!")
    dateTime = dateTime.replace(second=0, microsecond=0)
    
    #Unix conversion, in case we want to use this later.
    unix = time.mktime(dateTime.timetuple())
    
    dict = {
        "leaderId": os.getenv('DISCORD_ID'),
        "templateId": 10,
        "date": dateTime.strftime("%d-%m-%Y"),
        "time": dateTime.strftime("%H:%M"), 
        "title": fight
    }
    req = requests.post(url=URL, headers={"Authorization": APIKEY, "Content-Type": "application/json"}, json=dict)
    #print(req.json())

def main():
    load_configuration()
    
    URL = f"https://raid-helper.dev/api/v2/servers/{os.getenv('SERVER_ID')}/channels/{os.getenv('CHANNEL_ID')}/event"
    KEY = os.getenv('API_KEY')
    dt = datetime.now()

    next_wednesday = next_date(dt, 2)
    next_saturday = next_date(dt, 5)

    submit_raid_request("O8S - Wednesday", next_wednesday, URL, KEY)

    submit_raid_request("O8S - Saturday", next_saturday, URL, KEY)

if __name__=="__main__":
    main()
