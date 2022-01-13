class Poll:
    """
    Represents a poll
    """

    def __init__(self,id,broadcaster_id,broadcaster_name,broadcaster_login,title,choices,bits_voting_enabled,bits_per_vote,channel_points_voting_enabled,channel_points_per_vote,status,duration,started_at,ended_at=""):
        """
        Args:
            id (str): ID of the poll
            broadcaster_id (str): ID of the broadcaster
            broadcaster_name (str): Name of the broadcaster
            broadcaster_login (str): Login of the broadcaster
            title (str): Question displayed for the poll
            choices (list): The poll choices
            bits_voting_enabled (bool): Indicates if Bits can be used for voting
            bits_per_vote (int): Number of Bits required to vote once with Bits
            channel_points_voting_enabled (bool): Indicates if Channel Points can be used for voting
            channel_points_per_vote (int): Number of Channel Points required to vote once with Channel Points
            status (str): Poll status
                          Valid values are: ACTIVE, COMPLETED, TERMINATED, ARCHIVED, MODERATED, INVALID
            duration (int): Total duration for the poll (in seconds)
            started_at (str): UTC timestamp for the poll’s start time
            ended_at (str): UTC timestamp for the poll’s end time
        """

        self.id=id
        self.broadcaster_id=broadcaster_id
        self.broadcaster_name=broadcaster_name
        self.broadcaster_login=broadcaster_login
        self.title=title
        self.choices=choices
        self.bits_voting_enabled=bits_voting_enabled
        self.bits_per_vote=bits_per_vote
        self.channel_points_voting_enabled=channel_points_voting_enabled
        self.channel_points_per_vote=channel_points_per_vote
        self.status=status
        self.duration=duration
        self.started_at=started_at
        self.ended_at=ended_at