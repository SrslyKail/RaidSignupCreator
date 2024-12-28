#!/usr/bin/python3

'''
Keeping this chunk around because I found it useful to remind
myself what the package names are called in pip
organized as localName: pip_intaller_name
"requests":"requests",
"dotenv":"python-dotenv",
"dateutil":"python-dateutil"
'''

import os
from argparse import ArgumentParser, Namespace, BooleanOptionalAction
from pathlib import Path
from datetime import datetime, date
import requests
from dotenv import load_dotenv
from dateutil.relativedelta import relativedelta

namespace = Namespace()
all_sessions_info: dict

def get_raid_datetime(weekday: int, hour: int, minute: int) -> datetime:
    # Get the next instance of the given day
    next_date = datetime.today() + relativedelta(weekday=weekday)
    return next_date.replace(hour=hour, minute=minute, second=0, microsecond=0)

def load_configuration() -> None:
    """Loads the required environment variables from a .env file and checks that they loaded correctly.

    Raises:
        Exception: If the .env file is not located
        Exception: If a environment variable is missing
    """
    #User must supply the following environment variables via the .env file:
    required_env_variables = ["API_KEY", "SERVER_ID", "CHANNEL_ID", "DISCORD_ID"]
    missing_vars: list[str] = []

    #Get the current directory
    current_dir = Path(__file__).parent
    #Check the .env file exists
    if Path(current_dir / ".env").exists is False:
        raise Exception(f"Missing .env file. Check for a .env file at {current_dir}")
    
    #If it does, load the file
    load_dotenv()

    #Check the variables were loaded
    missing_vars = [
        variable for variable in required_env_variables
            if os.getenv(variable) is None
        ]

    #if something is missing, raise an exception so the user can add it
    if missing_vars:
        raise NameError(f"Missing required environment variables: {missing_vars}")
    
    parser: ArgumentParser = setup_parser()
    parser.parse_args(namespace=namespace)   
    
    return 

def setup_parser() -> ArgumentParser:
    parser: ArgumentParser = ArgumentParser()
    parser.add_argument(
    "-w",
    "--weekly",
    help="If you want to post all the raids for a single week at once",
    action=BooleanOptionalAction,
    dest="weekly",
    )
    
    return parser
    
    

def get_post_event_url(SERVER_ID:str, CHANNEL_ID:str):
    return f"https://raid-helper.dev/api/v2/servers/{SERVER_ID}/channels/{CHANNEL_ID}/event"

def get_events_info_url(SERVER_ID:str):
    return f"https://raid-helper.dev/api/v3/servers/{SERVER_ID}/events"

def get_next_date(raid: datetime | list[datetime]) -> datetime | None:
    """Gets the next date from a list of dates

    Args:
        raid (datetime | list[datetime]): a datetime or list of datetime objects.

    Returns:
        (datetime | None): The next date, or None if all the dates given were in the past.
    """
    
    if not isinstance(raid, list):
        raid = [raid]

    #Check for dates after today
    possible_dates: list[datetime] = [date for date in raid if datetime.now().date() < date.date()]

    if possible_dates is False:
        return None

    #Get the next one
    return min(possible_dates)


def get_posted_session_data(SERVER_ID:str, API_KEY:str) -> dict:
    """Gets the historic data for the raids that have been run

    Args:
        SERVER_ID (str): The Discord Server ID
        API_KEY (str): The Discord User API key

    Returns:
        dict: A dictionary of all the data.
    """
    events_url: str = get_events_info_url(SERVER_ID)
    sessions_info: dict = dict(
        requests.get(
            url=events_url,
            headers={"Authorization": API_KEY}
            ).json()
        )["postedEvents"]
    return sessions_info


def is_raid_day_available(next_date: datetime, sessions_info: dict) -> bool:
    """Checks if there is already a raid scheduled on the given day

    Args:
        next_date (datetime): a datetime object for the date you want to check
        sessions_info (dict): a dictionary of information about the next session; can be retrieved from get_posted_session_data()

    Returns:
        bool: True if the day is available, False if it is not
    """

    next_session = next_date.date()

    #If the date of the session is after the next_date, break
    for session in sessions_info:
        unix_session_time = session["startTime"]
        session_dateTime: date  = datetime.fromtimestamp(unix_session_time).date()

        #If the next session is before the one we want to make
        if session_dateTime < next_session:
            #We're clear to make a new one
            return True
        elif session_dateTime > next_session: #TODO: CB: Try removing this, I don't think we need it.
            #If its after the one we wanna make, keep checking
            continue
        elif session_dateTime == next_session:
            #If its the same, we dont want to make a new one
            return False
        else:
            continue
        
    return False #required to keep mypy happy


def get_last_session_title(all_sessions_info:dict) -> str:
    """
    Uses the title of the last session as the title of the next.
    
    Args:
        all_sessions_info (dict): A dictionary of all the raid sessions that have been undertaken. Use get_posted_session_data() to generate this.

    Returns:
        str: The title of the last session that was run.
    """
    #Get the last session by filtering for the 0th "postedEvents" in the given server
    last_posted_event  = all_sessions_info[0]

    #Get the title of the last session
    last_session_title = last_posted_event["title"]

    #Split it by [fight_name, date] and keep the fight_name
    next_session_title = last_session_title.split(" - ")[0]
    
    return next_session_title

def submit_raid_request(
    next_dateTime:datetime,
    sessions_info:dict,
    CHANNEL_ID:str,
    SERVER_ID:str,
    API_KEY:str
    ):
    
    #Unix conversion, in case we want to use this later.
    #unix = time.mktime(next_dateTime.timetuple())

    #Put together the data we want to post up
    dict = {
        "leaderId": os.getenv('DISCORD_ID'),
        "templateId": 10,
        "date": next_dateTime.strftime("%d-%m-%Y"),
        "time": next_dateTime.strftime("%H:%M"), 
        "title": f"{get_last_session_title(sessions_info)} - {next_dateTime.strftime('%A')}"
    }

    #Get the URL we want to post it to
    POST_URL = get_post_event_url(SERVER_ID, CHANNEL_ID)

    #Post it
    requests.post(
        url=POST_URL,
        headers={"Authorization": API_KEY, "Content-Type": "application/json"},
        json=dict
    )

def get_env_variable(variableName: str) -> str:
    env_var: str | None = os.getenv(variableName)
    if env_var is None:
        raise KeyError(f"Missing environment variable: {variableName}")
    return env_var

def main() -> None:
    global all_sessions_info
    load_configuration()
    print(namespace)
    
    saturday_raid = get_raid_datetime(
        weekday = 5,
        hour    = 13,
        minute  = 0
    )

    sunday_raid = get_raid_datetime(
        weekday = 6,
        hour    = 13,
        minute  = 0,
    )        
    
    raid_dates: list[datetime] = [saturday_raid, sunday_raid]

    CHANNEL_ID = get_env_variable('CHANNEL_ID')
    SERVER_ID  = get_env_variable('SERVER_ID')
    API_KEY    = get_env_variable('API_KEY')
    
    all_sessions_info = get_posted_session_data(SERVER_ID, API_KEY)
    
    if(namespace.weekly):
        create_raid_week(raid_dates=raid_dates, CHANNEL_ID=CHANNEL_ID, SERVER_ID=SERVER_ID, API_KEY=API_KEY)
    else:
        create_raid_day(raid_dates=raid_dates, CHANNEL_ID=CHANNEL_ID, SERVER_ID=SERVER_ID, API_KEY=API_KEY)

def create_raid_week(raid_dates: list[datetime],
    CHANNEL_ID:str,
    SERVER_ID:str,
    API_KEY:str):
    
    #sort dates to make sure we're posting the earliest date in the week first
    raid_dates.sort(key=lambda date: date.isocalendar().weekday)
    
    for raid_day in raid_dates:
        create_raid_day(raid_day, CHANNEL_ID, SERVER_ID, API_KEY)
    
    return

def create_raid_day(
    raid_dates: datetime | list[datetime],
    CHANNEL_ID:str,
    SERVER_ID:str,
    API_KEY:str):
    
    global all_sessions_info
    
    next_date: datetime | None
    next_date = get_next_date(raid_dates)
    
    if next_date is None:
        return

    if is_raid_day_available(next_date, all_sessions_info):
        #Submit next raid
        submit_raid_request(
            next_date, 
            all_sessions_info, 
            CHANNEL_ID, 
            SERVER_ID, 
            API_KEY
        )
    else:
        print(f"Event already exists on {next_date.strftime('%d-%m-%Y')}")

if __name__=="__main__":
    main()
