from dataclasses import dataclass
from datetime import datetime


@dataclass
class BlockedTerm:
    """
    Represents a blocked term

    Attributes:
        broadcaster_id (str): The broadcaster that owns the list of blocked terms
        moderator_id (str): The moderator that blocked the word or phrase from being used in the broadcaster’s chat room
        term_id (str): An ID that identifies this blocked term
        text (str): The blocked word or phrase
        created_at (datetime): The UTC date and time (in RFC3339 format) that the term was blocked
        updated_at (datetime): The UTC date and time (in RFC3339 format) that the term was updated
        expires_at (datetime): The UTC date and time (in RFC3339 format) that the blocked term is set to expire
    """

    broadcaster_id: str
    moderator_id: str
    term_id: str
    text: str
    created_at: datetime
    updated_at: datetime
    expires_at: datetime
