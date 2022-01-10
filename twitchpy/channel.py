import ssl
import socket

class Channel():
    """
    Represents a channel
    """

    def __init__(self,broadcaster_id,broadcaster_login,broadcaster_name,game_id,game_name,title,broadcaster_language="",delay=""):
        """
        Args:
            broadcaster_id (str): Twitch User ID of this channel owner
            broadcaster_login (str): Twitch user login of this channel owner
            broadcaster_name (str): Twitch user display name of this channel owner
            game_id (str): Current game ID being played on the channel
            game_name (str): Name of the game being played on the channel
            title (str): Title of the stream
            broadcaster_language (str, optional): Language of the channel
                                        A language value is either the ISO 639-1 two-letter code for a supported stream language or "other"
            delay (int, optional): Stream delay in seconds
        """

        self.broadcaster_id=broadcaster_id
        self.broadcaster_login=broadcaster_login
        self.broadcaster_name=broadcaster_name
        self.game_id=game_id
        self.game_name=game_name
        self.title=title
        self.broadcaster_language=broadcaster_language
        self.delay=delay