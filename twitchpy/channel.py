class Channel:
    """
    Represents a channel
    """

    def __init__(
        self,
        broadcaster_id: str,
        broadcaster_login: str,
        broadcaster_name: str,
        broadcaster_language: str,
        game_name: str,
        game_id: str,
        title: str,
        delay: int,
        tags: list[str],
        content_classification_labels: list[str],
        is_branded_content: bool,
    ):
        """
        Args:
            broadcaster_id (str): An ID that uniquely identifies the broadcaster
            broadcaster_login (str): The broadcaster’s login name
            broadcaster_name (str): The broadcaster’s display name
            broadcaster_language (str): The broadcaster’s preferred language
            game_name (str): The name of the game that the broadcaster is playing or last played
            game_id (str): An ID that uniquely identifies the game that the broadcaster is playing or last played
            title (str): The title of the stream that the broadcaster is currently streaming or last streamed
            delay (int): The value of the broadcaster’s stream delay setting, in seconds
            tags (list[str]): The tags applied to the channel
            content_classification_labels (list[str]): The CCLs applied to the channel
            is_branded_content (bool): Boolean flag indicating if the channel has branded content
        """

        self.broadcaster_id = broadcaster_id
        self.broadcaster_login = broadcaster_login
        self.broadcaster_name = broadcaster_name
        self.broadcaster_language = broadcaster_language
        self.game_name = game_name
        self.game_id = game_id
        self.title = title
        self.delay = delay
        self.tags = tags
        self.content_classification_labels = content_classification_labels
        self.is_branded_content = is_branded_content
