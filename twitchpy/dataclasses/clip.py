from dataclasses import dataclass


@dataclass
class Clip:
    """
    Represents a clip

    Attributes:
        clip_id (str): An ID that uniquely identifies the clip
        url (str): A URL to the clip
        embed_url (str): A URL that you can use in an iframe to embed the clip
        broadcaster_id (str): An ID that identifies the broadcaster that the video was clipped from
        broadcaster_name (str): The broadcaster’s display name
        creator_id (str): An ID that identifies the user that created the clip
        creator_name (str): The user’s display name
        video_id (str): An ID that identifies the video that the clip came from
        game_id (str): The ID of the game that was being played when the clip was created
        language (str): The ISO 639-1 two-letter language code that the broadcaster broadcasts in
        title (str): The title of the clip
        view_count (int): The number of times the clip has been viewed
        created_at (str): The date and time of when the clip was created
        thumbnail_url (str): A URL to a thumbnail image of the clip
        duration (float): The length of the clip, in seconds
            Precision is 0.1
        vod_offset (int): The zero-based offset, in seconds, to where the clip starts in the video (VOD)
        is_featured (bool): A Boolean value that indicates if the clip is featured or not
    """

    clip_id: str
    url: str
    embed_url: str
    broadcaster_id: str
    broadcaster_name: str
    creator_id: str
    creator_name: str
    video_id: str
    game_id: str
    language: str
    title: str
    view_count: int
    created_at: str
    thumbnail_url: str
    duration: float
    vod_offset: int
    is_featured: bool
