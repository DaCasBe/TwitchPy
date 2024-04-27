from dataclasses import dataclass

from ..dataclasses import User


@dataclass
class BitsLeaderboardLeader:
    """
    Represents a user in a Bits Leaderboard

    Attributes:
        user (User): The user on the leaderboard
        rank (int): The user’s position on the leaderboard
        score (int): The number of Bits the user has cheered
    """

    user: User
    rank: int
    score: int
