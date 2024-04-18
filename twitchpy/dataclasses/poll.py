from dataclasses import dataclass
from datetime import datetime

from ..dataclasses import Channel, PollChoice


@dataclass
class Poll:
    """
    Represents a poll

    Args:
        poll_id (str): ID of the poll
        broadcaster_id (str): ID of the broadcaster
        broadcaster_name (str): Name of the broadcaster
        broadcaster_login (str): Login of the broadcaster
        title (str): Question displayed for the poll
        choices (list): The poll choices
        channel_points_voting_enabled (bool): Indicates if Channel Points can be used for voting
        channel_points_per_vote (int): Number of Channel Points required to vote once with Channel Points
        status (str): Poll status
            Valid values are: ACTIVE, COMPLETED, TERMINATED, ARCHIVED, MODERATED, INVALID
        duration (int): Total duration for the poll (in seconds)
        started_at (str): UTC timestamp for the poll’s start time
        ended_at (str): UTC timestamp for the poll’s end time
    """

    poll_id: str
    channel: Channel
    title: str
    choices: list[PollChoice]
    channel_points_voting_enabled: bool
    channel_points_per_vote: int
    status: str
    duration: int
    started_at: datetime
    ended_at: datetime | None = None
