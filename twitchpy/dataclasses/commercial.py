from dataclasses import dataclass


@dataclass
class Commercial:
    """
    Represents a commercial

    Attributes:
        length (int): The length of the commercial
            Maximum: 180
        message (str): A message that indicates whether Twitch was able to serve an ad
        retry_after (int): The number of seconds you must wait before running another commercial
    """

    length: int
    message: str
    retry_after: int
