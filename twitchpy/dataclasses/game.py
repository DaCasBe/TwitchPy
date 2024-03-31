class Game:
    """
    Represents a Twitch category
    """

    def __init__(self, id: str, name: str, box_art_url: str = "", igdb_id: str = ""):
        """
        Args:
            id (int): An ID that identifies the category or game
            name (str): The category’s or game’s name
            box_art_url (str): A URL to the category’s or game’s box art
            igdb_id (str): The ID that IGDB uses to identify this game
        """

        self.id = id
        self.name = name
        self.box_art_url = box_art_url
        self.igdb_id = igdb_id
