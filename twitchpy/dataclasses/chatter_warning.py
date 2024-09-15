from dataclasses import dataclass


@dataclass
class ChatterWarning:
    """
    Represents a warning to a chat user

    Attributes:
        broadcaster_id (str): The ID of the channel in which the warning takes effect
        user_id (str): The ID of the warned user
        moderator_id (str): The ID of the user who applied the warning
        reason (str): The reason provided for warning
    """

    broadcaster_id: str
    user_id: str
    moderator_id: str
    reason: str
