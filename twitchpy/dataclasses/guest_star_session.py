from dataclasses import dataclass


@dataclass
class GuestStarSession:
    """
    Represents a Guest Star Session

    Attributes:
        guest_star_session_id (str): ID uniquely representing the Guest Star session
        guests (list[dict]): List of guests currently interacting with the Guest Star session
    """

    guest_star_session_id: str
    guests: list[dict]
