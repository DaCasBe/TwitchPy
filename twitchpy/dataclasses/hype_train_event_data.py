from dataclasses import dataclass
from datetime import datetime

from ..dataclasses import HypeTrainContribution


@dataclass
class HypeTrainEventData:
    """
    Represents the data of a Hype Train's event

    Attributes:
        broadcaster_id (str): The ID of the broadcaster that’s running the Hype Train
        cooldown_end_time (datetime): The UTC date and time (in RFC3339 format) that another Hype Train can start
        expires_at (datetime): The UTC date and time (in RFC3339 format) that the Hype Train ends
        goal (int): The value needed to reach the next level
        hype_train_id (str): An ID that identifies this Hype Train
        last_contribution (HypeTrainContribution): The most recent contribution towards the Hype Train’s goal
        level (int): The highest level that the Hype Train reached (the levels are 1 through 5)
        started_at (datetime): The UTC date and time (in RFC3339 format) that this Hype Train started
        top_contributions (list[HypeTrainContribution]): The top contributors for each contribution type
        total (int): The current total amount raised
    """

    broadcaster_id: str
    cooldown_end_time: datetime
    expires_at: datetime
    goal: int
    hype_train_id: str
    last_contribution: HypeTrainContribution
    level: int
    started_at: datetime
    top_contributions: list[HypeTrainContribution]
    total: int
