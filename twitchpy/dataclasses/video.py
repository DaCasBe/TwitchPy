from dataclasses import dataclass
from datetime import datetime

from ..dataclasses import Channel


@dataclass
class Video:
    """
    Represents a video

    Attributes:
        video_id (str): ID of the video
        stream_id (str): The ID of the stream that the video originated from
        channel (Channel): The channel that owns the video
        title (str): Title of the video
        description (str): Description of the video
        created_at (datetime): Date of creation of the video
        published_at (datetime): Date of publication of the video
        url (str): URL of the video
        thumbnail_url (str): URL of the preview image of the video
        viewable (str): Indicates whether the video is publicly viewable
        view_count (int): Number of times the video has been viewed
        language (str): Language of the video
        type (str): Type of the video
        duration (str): Duration of the video
        muted_segments (list[tuple[int, int]]): The segments that Twitch Audio Recognition muted
    """

    video_id: str
    stream_id: str
    channel: Channel
    title: str
    description: str
    created_at: datetime
    published_at: datetime
    url: str
    thumbnail_url: str
    viewable: str
    view_count: int
    language: str
    video_type: str
    duration: str
    muted_segments: list[tuple[int, int]]
