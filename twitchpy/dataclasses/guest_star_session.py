class GuestStarSession:
    """
    Represents a Guest Star Session
    """

    def __init__(self, id: str, guests: list[dict]):
        """
        The function initializes an object with an id and a list of guests.

        Args:
            id (str): ID uniquely representing the Guest Star session
            guests (list[dict]): List of guests currently interacting with the Guest Star session
        """

        self.id = id
        self.guests = guests
