class Stream:
    """
    Represents a stream
    """

    def __init__(
        self,
        stream_id: str,
        user_id: str,
        user_login: str,
        user_name: str,
        game_id: str,
        game_name: str,
        stream_type: str,
        title: str,
        tags: list[str],
        viewer_count: int,
        started_at: str,
        language: str,
        thumbnail_url: str,
        is_mature: bool,
    ):
        """
        Args:
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

        self.id = stream_id
        self.user_id = user_id
        self.user_login = user_login
        self.user_name = user_name
        self.game_id = game_id
        self.game_name = game_name
        self.type = stream_type
        self.title = title
        self.tags = tags
        self.viewer_count = viewer_count
        self.started_at = started_at
        self.language = language
        self.thumbnail_url = thumbnail_url
        self.is_mature = is_mature
