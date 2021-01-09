class Stream:
    """
    Represents a stream
    """

    def __init__(self,id,user_id,user_name,game_id,type,title,viewer_count,started_at,language,thumbnail_url,tag_ids):
        """
        Args:
            id (int): Stream's ID
            user_id (int): Channel's ID
            user_name (str): Channel's name
            game_id (int): Stream's category's ID
            type (str): Stream's status
            title (str): Stream's title
            viewer_count (int): Number of viewers
            started_at (str): Stream's start date and time
            language (str): Stream's language
            thumbnail_url (str): URL of the preview image
            tag_ids (list): IDs of the stream's tags
        """

        self.id=id
        self.user_id=user_id
        self.user_name=user_name
        self.game_id=game_id
        self.type=type
        self.title=title
        self.viewer_count=viewer_count
        self.started_at=started_at
        self.language=language
        self.thumbnail_url=thumbnail_url
        self.tag_ids=tag_ids