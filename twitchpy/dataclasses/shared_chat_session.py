from dataclasses import dataclass
from datetime import datetime


@dataclass
class SharedChatSession:
    """
    Represents a shared chat session

    Attributes:
        session_id: The unique identifier for the shared chat session
        host_broadcaster_id: The User ID of the host channel
        participants: The list of User ID's of the participants in the session
        created_at: The UTC date and time (in RFC3339 format) for when the session was created
        updated_at: The UTC date and time (in RFC3339 format) for when the session was last updated
    """

    session_id: str
    host_broadcaster_id: str
    participants: list[str]
    created_at: datetime
    updated_at: datetime
