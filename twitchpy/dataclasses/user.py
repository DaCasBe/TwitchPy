from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    """
    Represents an user

    Attributes:
        user_id (int): User's ID
        login (str): User's login
        display_name (str): User's name
        user_type (str | None): User type
        broadcaster_type (str | None): User's range
        description (str | None): User's description
        profile_image_url (str | None): URL of the user's profile image
        offline_image_url (str | None): URL of the image that is displayed when the user is not on stream
        view_count (int | None): Number of user viewers
        email (str | None): The user’s verified email address
        created_at (datetime | None): The UTC date and time that the user’s account was created
            The timestamp is in RFC3339 format
    """

    user_id: int
    login: str
    display_name: str
    user_type: str | None = None
    broadcaster_type: str | None = None
    description: str | None = None
    profile_image_url: str | None = None
    offline_image_url: str | None = None
    view_count: int | None = None
    email: str | None = None
    created_at: datetime | None = None
