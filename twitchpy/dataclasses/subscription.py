from dataclasses import dataclass

from ..dataclasses import Channel, User


@dataclass
class Subscription:
    """
    Represents a subscription

    Attributes:
        channel (Channel): The channel
        gifter (User): The user that gifted the subscription to the user
        is_gift (bool): A Boolean value that determines whether the subscription is a gift subscription
        tier (str): The type of subscription
            Possible values: 1000, 2000, 3000
        plan_name (str | None): The name of the subscription
        user (User | None): The subscribing user
    """

    channel: Channel
    gifter: User
    is_gift: bool
    tier: str
    plan_name: str | None = None
    user: User | None = None
