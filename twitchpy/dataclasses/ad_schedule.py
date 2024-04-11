from dataclasses import dataclass
from datetime import datetime


@dataclass
class AdSchedule:
    """
    Represents an ad schecule

    Attributes:
        snooze_count (int): The number of snoozes available for the broadcaster
        snooze_refresh_at (datetime): The UTC timestamp when the broadcaster will gain an additional snooze, in RFC3339 format
        next_ad_at (datetime): The UTC timestamp of the broadcaster’s next scheduled ad, in RFC3339 format
        duration (int): The length in seconds of the scheduled upcoming ad break
        last_ad_at (datetime): The UTC timestamp of the broadcaster’s last ad-break, in RFC3339 format
        preroll_free_time (int): The amount of pre-roll free time remaining for the channel in seconds
    """

    snooze_count: int
    snooze_refresh_at: datetime
    next_ad_at: datetime
    duration: int | None = None
    last_ad_at: datetime | None = None
    preroll_free_time: int | None = None
