class HypeTrainEvent:
    """
    Represents a Hype Train event
    """

    def __init__(self, id, event_type, event_timestamp, version, event_data):
        """
        Args:
            id (str): The distinct ID of the event
            event_type (str): Displays hypetrain.{event_name}, currently only hypetrain.progression
            event_timestamp (str): RFC3339 formatted timestamp of event
            version (str): Returns the version of the endpoint
            event_data (dict): The event data
        """

        self.id = id
        self.event_type = event_type
        self.event_timestamp = event_timestamp
        self.version = version
        self.event_data = event_data
