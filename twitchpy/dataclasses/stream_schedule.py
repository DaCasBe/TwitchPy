from dataclasses import dataclass
from datetime import datetime

from ..dataclasses import Channel, StreamScheduleSegment


@dataclass
class StreamSchedule:
    """
    Represents a stream schedule

    Attributes:
        segments (list[StreamScheduleSegment]): Scheduled broadcasts for this stream schedule
        channel (Channel): The channel that owns the broadcast schedule
        vacation (tuple[datetime, datetime]): If Vacation Mode is enabled, this includes start and end dates for the vacation
            If Vacation Mode is disabled, value is set to null
    """

    segments: list[StreamScheduleSegment]
    channel: Channel
    vacation: tuple[datetime, datetime]
