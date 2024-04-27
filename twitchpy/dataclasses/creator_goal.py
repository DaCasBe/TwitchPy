from dataclasses import dataclass
from datetime import datetime

from ..dataclasses import Channel


@dataclass
class CreatorGoal:
    """
    Represents a creator's goal

    Attributes:
        goal_id (str): An ID that identifies this goal
        channel (Channel): The channel where the goal was created
        type (str): The type of goal
            Possible values: follower, subscription, subscription_count, new_subscription, new_subscription_count
        description (str): A description of the goal
        current_amount (int): The goal’s current value
        target_amount (int): The goal’s target value
        created_at (datetime): The UTC date and time (in RFC3339 format) that the broadcaster created the goal
    """

    goal_id: str
    channel: Channel
    type: str
    description: str
    current_amount: int
    target_amount: int
    created_at: datetime
