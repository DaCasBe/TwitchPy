from dataclasses import dataclass
from datetime import datetime

from ..dataclasses import User


@dataclass
class ShieldModeStatus:
    """
    Represents the Shield Mode status

    Attributes:
        is_active (bool): A Boolean value that determines whether Shield Mode is active
        moderator (User): The moderator that last activated Shield Mode.
        last_activated_at (datetime): The UTC timestamp (in RFC3339 format) of when Shield Mode was last activated
    """

    is_active: bool
    moderator: User
    last_activated_at: datetime
