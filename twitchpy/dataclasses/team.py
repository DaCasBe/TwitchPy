from dataclasses import dataclass
from datetime import datetime

from ..dataclasses import User


@dataclass
class Team:
    """
    Represents a team

    Attributes:
        users (list[User]): Users in the team
        background_image_url (str): URL of the team background image
        banner (str): URL for the team banner
        created_at (datetime): Date and time the team was created
        updated_at (datetime): Date and time the team was last updated
        info (str): Team description
        thumbnail_url (str): Image URL for the team logo
        team_name (str): Team name
        team_display_name (str): Team display name
        team_id (str): Team ID
    """

    users: list[User]
    background_image_url: str
    banner: str
    created_at: datetime
    updated_at: datetime
    info: str
    thumbnail_url: str
    team_name: str
    team_display_name: str
    team_id: str
