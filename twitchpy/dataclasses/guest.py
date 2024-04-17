from dataclasses import dataclass
from datetime import datetime

from ..dataclasses import User


@dataclass
class Guest:
    """
    Represents a guest in a Guest Star session

    Attributes:
        slot_id (str): ID representing this guest’s slot assignment
        is_live (bool): Flag determining whether or not the guest is visible in the browser source in the host’s streaming software
        user (User): The user assigned to this slot
        volume (int): Value from 0 to 100 representing the host’s volume setting for this guest
        assigned_at (datetime): Timestamp when this guest was assigned a slot in the session
        audio_settings (dict): Information about the guest’s audio settings
        video_settings (dict): Information about the guest’s video settings
    """

    slot_id: str
    is_live: bool
    user: User
    volume: int
    assigned_at: datetime
    audio_settings: dict
    video_settings: dict
