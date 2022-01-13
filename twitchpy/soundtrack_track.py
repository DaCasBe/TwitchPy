class SoundtrackTrack:
    """
    Represents a track of a soundtrack
    """
    
    def __init__(self,track,source):
        """
        Args:
            track (dict): The track information
            source (dict): The source of the track
        """

        self.track=track
        self.source=source