class SoundtrackPlaylist:
    """
    Represents a playlist
    """
    
    def __init__(self, title, id, image_url, description, tracks=None):
        """
        Args:
            title (str): The playlist’s title
            id (str): The playlist’s ASIN (Amazon Standard Identification Number)
            image_url (str): A URL to the playlist’s image art
            description (str): A short description about the music that the playlist includes
            tracks (list): The list of tracks in the playlist
        """

        self.title=title
        self.id=id
        self.image_url=image_url
        self.description=description

        if tracks is None:
            self.tracks = list()
