from dataclasses import dataclass


@dataclass
class ChatSettings:
    """
    Represents a chat's settings

    Attributes:
        broadcaster_id (str): The ID of the broadcaster specified in the request
        emote_mode (bool): A Boolean value that determines whether chat messages must contain only emotes
        follower_mode (bool): A Boolean value that determines whether the broadcaster restricts the chat room to followers only
        follower_mode_duration (int): The length of time, in minutes, that users must follow the broadcaster before being able to participate in the chat room
        moderator_id (str): The moderator’s ID
        non_moderator_chat_delay (bool): A Boolean value that determines whether the broadcaster adds a short delay before chat messages appear in the chat room
        non_moderator_chat_delay_duration (int): The amount of time, in seconds, that messages are delayed before appearing in chat
        slow_mode (bool): A Boolean value that determines whether the broadcaster limits how often users in the chat room are allowed to send messages
        slow_mode_wait_time (int): The amount of time, in seconds, that users must wait between sending messages
        subscriber_mode (bool): A Boolean value that determines whether only users that subscribe to the broadcaster’s channel may talk in the chat room
        unique_chat_mode (bool): A Boolean value that determines whether the broadcaster requires users to post only unique messages in the chat room
    """

    broadcaster_id: str
    emote_mode: bool
    follower_mode: bool
    follower_mode_duration: int
    moderator_id: str
    non_moderator_chat_delay: bool
    non_moderator_chat_delay_duration: int
    slow_mode: bool
    slow_mode_wait_time: int
    subscriber_mode: bool
    unique_chat_mode: bool
