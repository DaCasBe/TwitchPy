from dataclasses import dataclass

from ..dataclasses import Reward


@dataclass
class Redemption:
    """
    Represents a reward redemption

    Args:
        broadcaster_name (str): The display name of the broadcaster that the reward belongs to
        broadcaster_id (str): The id of the broadcaster that the reward belongs to
        redemption_id (str): The ID of the redemption
        user_id (str): The ID of the user that redeemed the reward
        user_name (str): The display name of the user that redeemed the reward
        user_input (str): The user input provided
        status (str): One of UNFULFILLED, FULFILLED or CANCELED
        redeemed_at (str): Timestamp of when the reward was redeemed
        reward (Reward): The custom reward that was redeemed at the time it was redeemed
    """

    broadcaster_name: str
    broadcaster_id: str
    redemption_id: str
    user_id: str
    user_name: str
    user_input: str
    status: str
    redeemed_at: str
    reward: Reward
