from dataclasses import dataclass
from datetime import datetime


@dataclass
class DropEntitlement:
    """
    Represents a entitlement

    Attributes:
        drop_entitlement_id (str): An ID that identifies the entitlement
        benefit_id (str): An ID that identifies the benefit (reward)
        timestamp (datetime): The UTC date and time (in RFC3339 format) of when the entitlement was granted
        user_id (str): An ID that identifies the user who was granted the entitlement
        game_id (str): An ID that identifies the game the user was playing when the reward was entitled
        fulfillment_status (str): The entitlement’s fulfillment status
            Possible values: CLAIMED, FULFILLED
        last_updated (datetime): The UTC date and time (in RFC3339 format) of when the entitlement was last updated
    """

    drop_entitlement_id: str
    benefit_id: str
    timestamp: datetime
    user_id: str
    game_id: str
    fulfillment_status: str
    last_updated: datetime
