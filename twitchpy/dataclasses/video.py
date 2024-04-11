from dataclasses import dataclass


@dataclass
class Video:
    """
    Represents a video

    Attributes:
        id (str): ID of the video
        user_id (str): ID of the owner of the video
        user_name (str): User name of the owner of the video
        title (str): Title of the video
        description (str): Description of the video
        created_at (str): Date of creation of the video
        published_at (str): Date of publication of the video
        url (str): URL of the video
        thumbnail_url (str): URL of the preview image of the video
        viewable (str): Indicates whether the video is publicly viewable
        view_count (int): Number of times the video has been viewed
        language (str): Language of the video
        type (str): Type of the video
        duration (str): Duration of the video
    """

    video_id: str
    user_id: str
    user_name: str
    title: str
    description: str
    created_at: str
    published_at: str
    url: str
    thumbnail_url: str
    viewable: str
    view_count: int
    language: str
    video_type: str
    duration: str
