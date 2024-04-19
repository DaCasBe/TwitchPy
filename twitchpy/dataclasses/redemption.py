from dataclasses import dataclass
from datetime import datetime

from ..dataclasses import Channel, Reward, User


@dataclass
class Redemption:
    """
    Represents a reward redemption

    Args:
        channel (Channel): The channel that the reward belongs to
        redemption_id (str): The ID of the redemption
        user (User): The user that redeemed the reward
        user_input (str): The user input provided
        status (str): One of UNFULFILLED, FULFILLED or CANCELED
        redeemed_at (datetime): Timestamp of when the reward was redeemed
        reward (Reward): The custom reward that was redeemed at the time it was redeemed
    """

    channel: Channel
    redemption_id: str
    user: User
    user_input: str
    status: str
    redeemed_at: datetime
    reward: Reward
