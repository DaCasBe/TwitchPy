class Team:
    """
    Represents a team
    """

    def __init__(
        self,
        users,
        background_image_url,
        banner,
        created_at,
        updated_at,
        info,
        thumbnail_url,
        team_name,
        team_display_name,
        team_id,
    ):
        """
        Args:
            users (list): Users in the team
            background_image_url (str): URL of the team background image
            banner (str): URL for the team banner
            created_at (str): Date and time the team was created
            updated_at (str): Date and time the team was last updated
            info (str): Team description
            thumbnail_url (str): Image URL for the team logo
            team_name (str): Team name
            team_display_name (str): Team display name
            team_id (str): Team ID
        """

        self.users = users
        self.background_image_url = background_image_url
        self.banner = banner
        self.created_at = created_at
        self.updated_at = updated_at
        self.info = info
        self.thumbnail_url = thumbnail_url
        self.team_name = team_name
        self.team_display_name = team_display_name
        self.id = team_id
