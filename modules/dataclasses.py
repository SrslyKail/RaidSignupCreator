from dataclasses import dataclass
from typing import Any


@dataclass
class SessionInfo:
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
    leaderId: str
    templateId: int
    date: str
    time: str
    title: str
    advancedSettings: dict[str, Any]
