from dataclasses import dataclass


@dataclass
class Channel:
    """
    Represents a channel

    Attributes:
        broadcaster_id (str): An ID that uniquely identifies the broadcaster
        broadcaster_login (str): The broadcaster’s login name
        broadcaster_name (str): The broadcaster’s display name
        broadcaster_language (str): The broadcaster’s preferred language
        game_name (str): The name of the game that the broadcaster is playing or last played
        game_id (str): An ID that uniquely identifies the game that the broadcaster is playing or last played
        title (str): The title of the stream that the broadcaster is currently streaming or last streamed
        tags (list[str]): The tags applied to the channel
        delay (int): The value of the broadcaster’s stream delay setting, in seconds
        content_classification_labels (list[str]): The CCLs applied to the channel
        is_branded_content (bool): Boolean flag indicating if the channel has branded content
    """

    broadcaster_id: str
    broadcaster_login: str
    broadcaster_name: str
    broadcaster_language: str
    game_name: str
    game_id: str
    title: str
    tags: list[str]
    delay: int | None = None
    content_classification_labels: list[str] | None = None
    is_branded_content: bool | None = None
