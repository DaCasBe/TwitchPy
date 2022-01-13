class Clip:
    """
    Represents a clip
    """

    def __init__(self,id,url,embed_url,broadcaster_id,broadcaster_name,creator_id,creator_name,video_id,game_id,language,title,view_count,created_at,thumbnail_url,duration):
        """
        Args:
            id (str): ID of the clip being queried
            url (str): URL where the clip can be viewed
            embed_url (str): URL to embed the clip
            broadcaster_id (str): User ID of the stream from which the clip was created
            broadcaster_name (str): Display name corresponding to broadcaster_id
            creator_id (str): ID of the user who created the clip
            creator_name (str): Display name corresponding to creator_id
            video_id (str): ID of the video from which the clip was created
            game_id (str): ID of the game assigned to the stream when the clip was created
            language (str): Language of the stream from which the clip was created
                            A language value is either the ISO 639-1 two-letter code for a supported stream language or “other”
            title (str): Title of the clip
            view_count (int): Number of times the clip has been viewed
            created_at (str): Date when the clip was created
            thumbnail_url (str): URL of the clip thumbnail
            duration (float): Duration of the clip in seconds (up to 0.1 precision)
        """

        self.id=id
        self.url=url
        self.embed_url=embed_url
        self.broadcaster_id=broadcaster_id
        self.broadcaster_name=broadcaster_name
        self.creator_id=creator_id
        self.creator_name=creator_name
        self.video_id=video_id
        self.game_id=game_id
        self.language=language
        self.title=title
        self.view_count=view_count
        self.created_at=created_at
        self.thumbnail_url=thumbnail_url
        self.duration=duration