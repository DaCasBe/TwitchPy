from dataclasses import dataclass

from ..dataclasses import Guest


@dataclass
class GuestStarSession:
    """
    Represents a Guest Star Session

    Attributes:
        guest_star_session_id (str): ID uniquely representing the Guest Star session
        guests (list[Guest]): List of guests currently interacting with the Guest Star session
    """

    guest_star_session_id: str
    guests: list[Guest]
