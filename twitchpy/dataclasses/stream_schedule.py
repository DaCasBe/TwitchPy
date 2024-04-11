from dataclasses import dataclass


@dataclass
class StreamSchedule:
    """
    Represents a stream schedule

    Attributes:
        segments (list[dict]): Scheduled broadcasts for this stream schedule
        broadcaster_id (str): User ID of the broadcaster
        broadcaster_name (str): Display name of the broadcaster
        broadcaster_login (str): Login of the broadcaster
        vacation (dict): If Vacation Mode is enabled, this includes start and end dates for the vacation
            If Vacation Mode is disabled, value is set to null
    """

    segments: list[dict]
    broadcaster_id: str
    broadcaster_name: str
    broadcaster_login: str
    vacation: dict
