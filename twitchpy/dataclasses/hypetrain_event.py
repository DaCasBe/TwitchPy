from dataclasses import dataclass


@dataclass
class HypeTrainEvent:
    """
    Represents a Hype Train event

    Attributes:
        event_id (str): The distinct ID of the event
        event_type (str): Displays hypetrain.{event_name}, currently only hypetrain.progression
        event_timestamp (str): RFC3339 formatted timestamp of event
        version (str): Returns the version of the endpoint
        event_data (dict): The event data
    """

    event_id: str
    event_type: str
    event_timestamp: str
    version: str
    event_data: dict
