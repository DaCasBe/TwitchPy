from dataclasses import dataclass


@dataclass
class Badge:
    """
    Represents a chat badge

    Attributes:
        set_id (str): ID for the chat badge set
        versions (list[dict]): Chat badge versions for the set
    """

    set_id: str
    versions: list[dict]
