class StreamSchedule:
    """
    Represents a stream schedule
    """

    def __init__(
        self, segments, broadcaster_id, broadcaster_name, broadcaster_login, vacation
    ):
        """
        Args:
            segments (list): Scheduled broadcasts for this stream schedule
            broadcaster_id (str): User ID of the broadcaster
            broadcaster_name (str): Display name of the broadcaster
            broadcaster_login (str): Login of the broadcaster
            vacation (dict): If Vacation Mode is enabled, this includes start and end dates for the vacation
                             If Vacation Mode is disabled, value is set to null
        """

        self.segments = segments
        self.broadcaster_id = broadcaster_id
        self.broadcaster_name = broadcaster_name
        self.broadcaster_login = broadcaster_login
        self.vacation = vacation
