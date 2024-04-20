from dataclasses import dataclass
from datetime import datetime


@dataclass
class Transport:
    """
    Represents a transport for sending notifications

    Attributes:
        method (str): The transport method
            Possible values are: webhook, websocket, conduit
        callback (str): The callback URL where the notifications are sent
        session_id (str): An ID that identifies the WebSocket that notifications are sent to
        connected_at (datetime): The UTC date and time that the WebSocket connection was established
        disconnected_at (datetime | None): The UTC date and time that the WebSocket connection was lost
        conduit_id (str | None): An ID that identifies the conduit to send notifications to
    """

    method: str
    callback: str
    session_id: str
    connected_at: datetime
    disconnected_at: datetime | None = None
    conduit_id: str | None = None
