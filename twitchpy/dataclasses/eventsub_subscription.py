from dataclasses import dataclass
from datetime import datetime

from ..dataclasses import Transport


@dataclass
class EventSubSubscription:
    """
    Represents an EventSub subscription

    Attributes:
        id (str): An ID that identifies the subscription
        status (str): The subscription’s status
            Possible values are: enabled, webhook_callback_verification_pending, webhook_callback_verification_failed, notification_failures_exceeded, authorization_revoked, user_removed
        type (str): The subscription’s type
        version (str): The version of the subscription type
        condition (dict): The subscription’s parameter values
        created_at (str): The RFC 3339 timestamp indicating when the subscription was created
        transport (Transport): The transport details used to send you notifications
        cost (int): The amount that the subscription counts against your limit
    """

    subscription_id: str
    status: str
    subscription_type: str
    version: str
    condition: dict
    created_at: datetime
    transport: Transport
    cost: int
