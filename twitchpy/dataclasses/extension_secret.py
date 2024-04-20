from dataclasses import dataclass
from datetime import datetime


@dataclass
class ExtensionSecret:
    """
    Represents an extension's secret

    Attributes:
        content (str): The raw secret that you use with JWT encoding
        active_at (datetime): The UTC date and time (in RFC3339 format) that you may begin using this secret to sign a JWT
        expires_at (datetime): The UTC date and time (in RFC3339 format) that you must stop using this secret to decode a JWT
    """

    content: str
    active_at: datetime
    expires_at: datetime
