from dataclasses import dataclass

from ..dataclasses import User


@dataclass
class Predictor:
    """
    Represents a predictor in a prediction

    Attributes:
        user (User): The viewer
        channel_points_used (int): The number of Channel Points the viewer spent
        channel_points_won (int): The number of Channel Points distributed to the viewer
    """

    user: User
    channel_points_used: int
    channel_points_won: int
