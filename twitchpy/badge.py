class Badge:
    """
    Represents a chat badge
    """

    def __init__(self,set_id,versions):
        """
        Args:
            set_id (str): ID for the chat badge set
            versions (list): Chat badge versions for the set
        """

        self.set_id=set_id
        self.versions=versions