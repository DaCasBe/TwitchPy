from dataclasses import dataclass
from datetime import datetime

from ..dataclasses import Channel, Game


@dataclass
class Stream:
    """
    Represents a stream

    Attributes:
        stream_id (str): An ID that identifies the stream
        channel (Channel): The channel that is broadcasting the stream
        game (Game): The category or game being played
        stream_type (str): The type of stream
        title (str): The stream’s title
        tags (list[str]): The tags applied to the stream
        viewer_count (int): The number of users watching the stream
        started_at (str): The UTC date and time (in RFC3339 format) of when the broadcast began
        language (str): The language that the stream uses
        thumbnail_url (str): A URL to an image of a frame from the last 5 minutes of the stream
        is_mature (bool): A Boolean value that indicates whether the stream is meant for mature audiences
    """

    stream_id: str
    channel: Channel
    game: Game
    stream_type: str
    title: str
    tags: list[str]
    viewer_count: int
    started_at: datetime
    language: str
    thumbnail_url: str
    is_mature: bool
