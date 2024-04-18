from dataclasses import dataclass
from datetime import datetime

from ..dataclasses import User


@dataclass
class BannedUser:
    """
    Represents a user that were banned or put in a timeout

    Attributes:
        user (User): The banned user
        expires_at (datetime): The UTC date and time (in RFC3339 format) of when the timeout expires, or an empty string if the user is permanently banned
        created_at (datetime): The UTC date and time (in RFC3339 format) of when the user was banned
        reason (str): The reason the user was banned or put in a timeout if the moderator provided one
        moderator (User): The moderator that banned the user or put them in a timeout
    """

    user: User
    expires_at: datetime
    created_at: datetime
    reason: str
    moderator: User
