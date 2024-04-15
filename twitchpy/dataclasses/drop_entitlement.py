from dataclasses import dataclass
from datetime import datetime


@dataclass
class DropEntitlement:
    drop_entitlement_id: str
    benefit_id: str
    timestamp: datetime
    user_id: str
    game_id: str
    fulfillment_status: str
    last_updated: datetime
