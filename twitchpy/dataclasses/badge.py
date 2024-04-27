from dataclasses import dataclass

from ..dataclasses import BadgeVersion


@dataclass
class Badge:
    """
    Represents a chat badge

    Attributes:
        set_id (str): ID for the chat badge set
        versions (list[BadgeVersion]): Chat badge versions for the set
    """

    set_id: str
    versions: list[BadgeVersion]
