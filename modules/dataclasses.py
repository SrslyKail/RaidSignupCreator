from dataclasses import dataclass
from typing import Any


@dataclass
class SessionInfo:
    """This dataclass is meant to hold data from the raid-helper API.

    It's primary use in auto-complete help in the IDE, and ensuring we know what data is suppose to be returned upon a successful API call.
    """

    color: str
    description: str
    title: str
    templateId: int
    signUpCount: int
    leaderId: str
    lastUpdated: int
    leaderName: str
    closeTime: int
    startTime: int
    endTime: int
    id: str
    channelId: str


@dataclass
class NewRaidPost:
    """Dataclass that contains the required data to be passed to the raid-helper API."""

    leaderId: str
    templateId: int
    date: str
    time: str
    title: str
    advancedSettings: dict[str, Any]
