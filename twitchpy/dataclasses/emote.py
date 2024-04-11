from dataclasses import dataclass


@dataclass
class Emote:
    """
    Represents an emote

    Attributes:
        emote_id (str): An ID that identifies the emote
        name (str): The name of the emote
            This is the name that viewers type in the chat window to get the emote to appear
        images (dict): Contains the image URLs for the emote
            These image URLs will always provide a static (i.e., non-animated) emote image with a light background
        emote_format (list[str]): The formats that the emote is available in
            The possible formats are: animated, static
        scale (list[str]): The sizes that the emote is available in
            Possible sizes are: 1.0, 2.0, 3.0
        theme_mode (list[str]): The background themes that the emote is available in
            Possible themes are: dark, light
        tier (str): The subscriber tier at which the emote is unlocked
            This field contains the tier information only if emote_type is set to subscriptions, otherwise, it’s an empty string
        emote_type (str): The type of emote
            The possible values are: bitstier, follower, subscriptions
        emote_set_id (str): An ID that identifies the emote set that the emote belongs to
    """

    emote_id: str
    name: str
    images: dict
    emote_format: list[str]
    scale: list[str]
    theme_mode: list[str]
    tier: str = ""
    emote_type: str = ""
    emote_set_id: str = ""
