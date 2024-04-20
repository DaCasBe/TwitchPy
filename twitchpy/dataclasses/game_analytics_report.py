from dataclasses import dataclass
from datetime import datetime


@dataclass
class GameAnalyticsReport:
    """
    Represents an analytics report for a game

    Attributes:
        game_id (str): An ID that identifies the game that the report was generated for
        url (str): The URL that you use to download the report
        type (str): The type of report
        started_at (datetime): The reporting window’s start date
        ended_at (datetime): The reporting window’s end date
    """

    game_id: str
    url: str
    type: str
    started_at: datetime
    ended_at: datetime
