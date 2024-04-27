from dataclasses import dataclass
from datetime import datetime

from ..dataclasses import Channel, User


@dataclass
class UnbanRequest:
    """
    Represents an unban request

    Attributes:
        request_id (str): Unban request ID
        channel (Channel): Channel that is receiving the unban request
        moderator (User): Moderator who approved/denied the request
        user (User): User who is asking for an unban
        text (str): Text of the request from the requesting user
        status (str): Status of the request
            Possible values: pending, approved, denied, acknowledged, canceled
        created_at (datetime): Timestamp of when the unban request was created
        resolved_at (datetime): Timestamp of when moderator/broadcaster approved or denied the request
        resolution_text (str): Text input by the resolver (moderator) of the unban request
    """

    request_id: str
    channel: Channel
    moderator: User
    user: User
    text: str
    status: str
    created_at: datetime
    resolved_at: datetime
    resolution_text: str
