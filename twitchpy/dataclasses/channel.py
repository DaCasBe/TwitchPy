from dataclasses import dataclass

from ..dataclasses import Game, User


@dataclass
class Channel:
    """
    Represents a channel

    Attributes:
        user (User): The user associated with the channel
        broadcaster_language (str | None): The broadcaster’s preferred language
        game (Game | None): The game that the broadcaster is playing or last played
        title (str | None): The title of the stream that the broadcaster is currently streaming or last streamed
        tags (list[str] | None): The tags applied to the channel
        delay (int | None): The value of the broadcaster’s stream delay setting, in seconds
        content_classification_labels (list[str] | None): The CCLs applied to the channel
        is_branded_content (bool | None): Boolean flag indicating if the channel has branded content
    """

    user: User
    broadcaster_language: str | None = None
    game: Game | None = None
    title: str | None = None
    tags: list[str] | None = None
    delay: int | None = None
    content_classification_labels: list[str] | None = None
    is_branded_content: bool | None = None
