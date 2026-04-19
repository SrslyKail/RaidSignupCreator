#!/usr/bin/python3

"""
Keeping this chunk around because I found it useful to remind
myself what the package names are called in pip
organized as localName: pip_intaller_name
"requests":"requests",
"dotenv":"python-dotenv",
"dateutil":"python-dateutil"
"""

import requests
from dataclasses import asdict
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from modules.dataclasses import NewRaidPost, SessionInfo
from modules.configuration import Config, ConfigFactory


class Raid:
    def __init__(self) -> None: ...


def get_raid_datetime(weekday: int, hour: int, minute: int) -> datetime:
    # Get the next instance of the given day
    today = datetime.today()
    next_date = today + relativedelta(weekday=weekday)
    # Lets us run it on the same day as a raid event and get the event for next week rather than the current week.
    if next_date == today:
        next_date += relativedelta(weeks=1)
    return next_date.replace(hour=hour, minute=minute, second=0, microsecond=0)


def get_server_route(API_ROUTE: str, SERVER_ID: str) -> str:
    return f"{API_ROUTE}/servers/{SERVER_ID}"


def get_post_event_url(SERVER_ROUTE: str, CHANNEL_ID: str) -> str:
    return f"{SERVER_ROUTE}/channels/{CHANNEL_ID}/event"


def get_events_info_url(SERVER_ROUTE: str) -> str:
    return f"{SERVER_ROUTE}/events"


def get_next_date(raid: datetime | list[datetime]) -> datetime | None:
    """Gets the next date from a list of dates

    Args:
        raid (datetime | list[datetime]): a datetime or list of datetime objects.

    Returns:
        (datetime | None): The next date, or None if all the dates given were in the past.
    """

    # Ensure we have a list
    if not isinstance(raid, list):
        raid = [raid]

    # Check for dates after today
    possible_dates: list[datetime] = [
        date for date in raid if datetime.now().date() < date.date()
    ]

    if len(possible_dates) <= 0:
        return None

    # Get the next one
    return min(possible_dates)


def get_posted_session_data(SERVER_ROUTE: str, API_KEY: str) -> list[SessionInfo]:
    """Gets the historic data for the raids that have been run

    Args:
        SERVER_ID (str): The Discord Server ID
        API_KEY (str): The Discord User API key

    Returns:
        dict: A dictionary of all the data.
    """
    events_url: str = get_events_info_url(SERVER_ROUTE)
    raw_res = requests.get(url=events_url, headers={"Authorization": API_KEY})
    postedEvents = dict(raw_res.json())["postedEvents"]
    sessions_info = [SessionInfo(**event) for event in postedEvents]
    return sessions_info


def is_raid_day_available(
    next_date: datetime, sessions_info: list[SessionInfo]
) -> bool:
    """Checks if there is already a raid scheduled on the given day

    Args:
        next_date (datetime): a datetime object for the date you want to check
        sessions_info (dict): a dictionary of information about the next session; can be retrieved from get_posted_session_data()

    Returns:
        bool: True if the day is available, False if it is not
    """

    next_session = next_date.date()

    # If the date of the session is after the next_date, break
    for session in sessions_info:
        unix_session_time = session.startTime
        session_dateTime: date = datetime.fromtimestamp(unix_session_time).date()

        # If the next session is before the one we want to make
        if session_dateTime < next_session:
            # We're clear to make a new one
            return True
        elif (
            session_dateTime > next_session
        ):  # TODO: CB: Try removing this, I don't think we need it.
            # If its after the one we wanna make, keep checking
            continue
        elif session_dateTime == next_session:
            # If its the same, we dont want to make a new one
            return False
        else:
            continue

    return False  # required to keep mypy happy


def get_last_session_title(all_sessions_info: list[SessionInfo]) -> str:
    """
    Uses the title of the last session as the title of the next.

    Args:
        all_sessions_info (dict): A dictionary of all the raid sessions that have been undertaken. Use get_posted_session_data() to generate this.

    Returns:
        str: The title of the last session that was run.
    """
    # Get the last session by filtering for the 0th "postedEvents" in the given server
    last_posted_event = all_sessions_info[0]

    # Get the title of the last session
    last_session_title = last_posted_event.title

    # Split it by [fight_name, date] and keep the fight_name
    next_session_title = last_session_title.split(" - ")[0]

    return next_session_title


def submit_raid_request(
    next_dateTime: datetime, all_sessions_info: list[SessionInfo], config: Config
) -> None:
    # Unix conversion, in case we want to use this later.
    # unix = time.mktime(next_dateTime.timetuple())

    # Put together the data we want to post up
    raidPost = NewRaidPost(
        leaderId=config.DISCORD_ID,
        templateId=10,
        date=next_dateTime.strftime("%d-%m-%Y"),
        time=next_dateTime.strftime("%H:%M"),
        title=f"{get_last_session_title(all_sessions_info)} - {next_dateTime.strftime('%A')}",
        advancedSettings={"lower_limit": 8},
    )

    # Get the URL we want to post it to
    SERVER_ROUTE: str = get_server_route(config.API_ROUTE, config.SERVER_ID)
    POST_URL = get_post_event_url(SERVER_ROUTE, config.CHANNEL_ID)

    # Post it
    res = requests.post(
        url=POST_URL,
        headers={"Authorization": config.API_KEY, "Content-Type": "application/json"},
        json=asdict(raidPost),
    )
    if res.status_code == 200:
        print(f"Created event on {raidPost.date}")


def create_raid_week(
    raid_dates: list[datetime],
    config: Config,
    all_sessions_info: list[SessionInfo],
):
    # sort dates to make sure we're posting the earliest date in the week first
    raid_dates.sort(key=lambda date: date.isocalendar().weekday)

    for raid_day in raid_dates:
        create_raid_day(
            raid_day,
            config,
            all_sessions_info,
        )


def create_raid_day(
    raid_dates: datetime | list[datetime],
    config: Config,
    all_sessions_info: list[SessionInfo],
) -> None:

    next_date: datetime | None
    next_date = get_next_date(raid_dates)

    if next_date is None:
        print("Date is none!")
        return

    if is_raid_day_available(next_date, all_sessions_info):
        # Submit next raid
        submit_raid_request(next_date, all_sessions_info, config)
    else:
        print(f"Event already exists on {next_date.strftime('%d-%m-%Y')}")


def main() -> None:
    config: Config = ConfigFactory.createConfig()

    saturday_raid = get_raid_datetime(weekday=5, hour=12, minute=0)

    sunday_raid = get_raid_datetime(
        weekday=6,
        hour=12,
        minute=0,
    )

    raid_dates: list[datetime] = [saturday_raid, sunday_raid]
    SERVER_ROUTE: str = get_server_route(config.API_ROUTE, config.SERVER_ID)

    all_sessions_info: list[SessionInfo] = get_posted_session_data(
        SERVER_ROUTE, config.API_KEY
    )

    if config.WEEKLY:
        create_raid_week(
            raid_dates=raid_dates,
            config=config,
            all_sessions_info=all_sessions_info,
        )
    else:
        create_raid_day(
            raid_dates=raid_dates,
            config=config,
            all_sessions_info=all_sessions_info,
        )


if __name__ == "__main__":
    main()
