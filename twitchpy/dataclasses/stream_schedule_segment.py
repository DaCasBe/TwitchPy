from dataclasses import dataclass
from datetime import datetime

from ..dataclasses import Game


@dataclass
class StreamScheduleSegment:
    """
    Represents a scheduled broadcast in a channel's streaming schedule

    Attributes:
        segment_id (str): An ID that identifies this broadcast segment
        start_time (datetime): The UTC date and time (in RFC3339 format) of when the broadcast starts
        end_time (datetime): The UTC date and time (in RFC3339 format) of when the broadcast ends
        title (str): The broadcast segment’s title
        canceled_until (datetime): Indicates whether the broadcaster canceled this segment of a recurring broadcast
        category (Game): The type of content that the broadcaster plans to stream
        is_recurring (bool): A Boolean value that determines whether the broadcast is part of a recurring series that streams at the same time each week or is a one-time broadcast
    """

    segment_id: str
    start_time: datetime
    end_time: datetime
    title: str
    canceled_until: datetime
    category: Game
    is_recurring: bool
