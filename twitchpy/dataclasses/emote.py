from dataclasses import dataclass


@dataclass
class Emote:
    """
    Represents an emote

    Attributes:
        emote_id (str): An ID that identifies the emote
        name (str): The name of the emote
            This is the name that viewers type in the chat window to get the emote to appear
        emote_format (list[str]): The formats that the emote is available in
            The possible formats are: animated, static
        scale (list[str]): The sizes that the emote is available in
            Possible sizes are: 1.0, 2.0, 3.0
        theme_mode (list[str]): The background themes that the emote is available in
            Possible themes are: dark, light
        images (dict | None): Contains the image URLs for the emote
            These image URLs will always provide a static (i.e., non-animated) emote image with a light background
        tier (str | None): The subscriber tier at which the emote is unlocked
            This field contains the tier information only if emote_type is set to subscriptions, otherwise, it’s an empty string
        emote_type (str | None): The type of emote
            The possible values are: bitstier, follower, subscriptions
        emote_set_id (str | None): An ID that identifies the emote set that the emote belongs to
        owner_id (str | None): The ID of the broadcaster who owns the emote
    """

    emote_id: str
    name: str
    emote_format: list[str]
    scale: list[str]
    theme_mode: list[str]
    images: dict | None = None
    tier: str | None = None
    emote_type: str | None = None
    emote_set_id: str | None = None
    owner_id: str | None = None
