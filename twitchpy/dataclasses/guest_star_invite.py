from dataclasses import dataclass
from datetime import datetime


@dataclass
class GuestStarInvite:
    """
    Represents a Guest Star's invite

    Attributes:
        user_id (str): Twitch User ID corresponding to the invited guest
        invited_at (datetime): Timestamp when this user was invited to the session
        status (str): Status representing the invited user’s join state
            Possible values: INVITED, ACCEPTED, READY
        is_video_enabled (bool): Flag signaling that the invited user has chosen to disable their local video device
        is_audio_enabled (bool): Flag signaling that the invited user has chosen to disable their local audio device
        is_video_available (bool): Flag signaling that the invited user has a video device available for sharing
        is_audio_available (bool): Flag signaling that the invited user has an audio device available for sharing
    """

    user_id: str
    invited_at: datetime
    status: str
    is_video_enabled: bool
    is_audio_enabled: bool
    is_video_available: bool
    is_audio_available: bool
