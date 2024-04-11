from dataclasses import dataclass


@dataclass
class User:
    """
    Represents an user

    Attributes:
        id (int): User's ID
        login (str): User's login
        display_name (str): User's name
        type (str): User type
        broadcaster_type (str): User's range
        description (str): User's description
        profile_image_url (str): URL of the user's profile image
        offline_image_url (str): URL of the image that is displayed when the user is not on stream
        view_count (int): Number of user viewers
    """

    user_id: int
    login: str
    display_name: str
    user_type: str = ""
    broadcaster_type: str = ""
    description: str = ""
    profile_image_url: str = ""
    offline_image_url: str = ""
    view_count: int = 0
