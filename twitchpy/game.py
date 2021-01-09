class Game:
    """
    Represents a Twitch category
    """

    def __init__(self,id,name,box_art_url):
        """
        Args:
            id (int): Category's ID
            name (str): Category's name
            box_art_url (str): URL of the category's image
        """

        self.id=id
        self.name=name
        self.box_art_url=box_art_url