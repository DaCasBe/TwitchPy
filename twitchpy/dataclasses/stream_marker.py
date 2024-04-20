from dataclasses import dataclass
from datetime import datetime


@dataclass
class StreamMarker:
    """
    Represents a marker in a stream

    Attributes:
        marker_id (str): An ID that identifies this marker
        created_at (datetime): The UTC date and time (in RFC3339 format) of when the user created the marker
        position_seconds (int): The relative offset (in seconds) of the marker from the beginning of the stream
        description (str): A description that the user gave the marker to help them remember why they marked the location
    """

    marker_id: str
    created_at: datetime
    position_seconds: int
    description: str
