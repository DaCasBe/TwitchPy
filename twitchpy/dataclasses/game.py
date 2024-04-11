from dataclasses import dataclass


@dataclass
class Game:
    """
    Represents a Twitch category

    Attributes:
        game_id (int): An ID that identifies the category or game
        name (str): The category’s or game’s name
        box_art_url (str): A URL to the category’s or game’s box art
        igdb_id (str): The ID that IGDB uses to identify this game
    """

    game_id: str
    name: str
    box_art_url: str = ""
    igdb_id: str = ""
