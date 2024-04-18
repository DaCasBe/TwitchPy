from dataclasses import dataclass


@dataclass
class PollChoice:
    """
    Represents a choice in a poll

    Attributes:
        choice_id (str): An ID that identifies this choice
        title (str): The choice's title
            The title may contain a maximum of 25 characters
        votes (int): The total number of votes cast for this choice
        channel_points_votes (int): The number of votes cast using Channel Points
    """

    choice_id: str
    title: str
    votes: int
    channel_points_votes: int
