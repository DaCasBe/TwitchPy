class User:
    """
    Represents an user
    """

    def __init__(
        self,
        id,
        login,
        display_name,
        type="",
        broadcaster_type="",
        description="",
        profile_image_url="",
        offline_image_url="",
        view_count=0,
    ):
        """
        Args:
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

        self.id = id
        self.login = login
        self.display_name = display_name
        self.type = type
        self.broadcaster_type = broadcaster_type
        self.description = description
        self.profile_image_url = profile_image_url
        self.offline_image_url = offline_image_url
        self.view_count = view_count
