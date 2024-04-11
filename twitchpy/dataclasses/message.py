from dataclasses import dataclass


@dataclass
class Message:
    """
    Represents a message

    Attributes:
        prefix (str): Message's prefix
        user (str): User who has sent the message
        channel (str): Channel on which the message was sent
        irc_command (str): IRC command related to the message
        irc_args (str): IRC command's arguments
        text (str): Message's text
        text_command (str): Command related to the message
        text_args (str): Command's arguments
    """

    prefix: str
    user: str
    channel: str
    irc_command: str
    irc_args: str
    text: str
    text_command: str
    text_args: str
