from dataclasses import dataclass


@dataclass
class Stream:
    """
    Represents a stream

    Attributes:
        stream_id (str): An ID that identifies the stream
        user_id (str): The ID of the user that’s broadcasting the stream
        user_login (str): The user’s login name
        user_name (str): The user’s display name
        game_id (str): The ID of the category or game being played
        game_name (str): The name of the category or game being played
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
    user_id: str
    user_login: str
    user_name: str
    game_id: str
    game_name: str
    stream_type: str
    title: str
    tags: list[str]
    viewer_count: int
    started_at: str
    language: str
    thumbnail_url: str
    is_mature: bool
