from dataclasses import dataclass


@dataclass
class Message:
    """
    Represents a message

    Attributes:
        prefix (str | None): Message's prefix
        user (str | None): User who has sent the message
        channel (str | None): Channel on which the message was sent
        irc_command (str | None): IRC command related to the message
        irc_tags (dict | None): IRC command's tags
        irc_args (list[str] | None): IRC command's arguments
        text (str | None): Message's text
        text_command (str | None): Command related to the message
        text_args (list[str] | None): Command's arguments
    """

    prefix: str | None = None
    user: str | None = None
    channel: str | None = None
    irc_command: str | None = None
    irc_tags: dict | None = None
    irc_args: list[str] | None = None
    text: str | None = None
    text_command: str | None = None
    text_args: list[str] | None = None
