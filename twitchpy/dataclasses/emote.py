class Emote:
    """
    Represents an emote
    """

    def __init__(
        self,
        emote_id,
        name,
        images,
        emote_format,
        scale,
        theme_mode,
        tier="",
        emote_type="",
        emote_set_id="",
    ):
        """
        Args:
            emote_id (str): An ID that identifies the emote
            name (str): The name of the emote
                        This is the name that viewers type in the chat window to get the emote to appear
            images (dict): Contains the image URLs for the emote
                           These image URLs will always provide a static (i.e., non-animated) emote image with a light background
            emote_format (list): The formats that the emote is available in
                           The possible formats are: animated, static
            scale (list): The sizes that the emote is available in
                          Possible sizes are: 1.0, 2.0, 3.0
            theme_mode (list): The background themes that the emote is available in
                               Possible themes are: dark, light
            tier (str, optional): The subscriber tier at which the emote is unlocked
                        This field contains the tier information only if emote_type is set to subscriptions, otherwise, it’s an empty string
            emote_type (str, optional): The type of emote
                              The possible values are: bitstier, follower, subscriptions
            emote_set_id (str, optional): An ID that identifies the emote set that the emote belongs to
        """

        self.id = emote_id
        self.name = name
        self.images = images
        self.format = emote_format
        self.scale = scale
        self.theme_mode = theme_mode
        self.tier = tier
        self.emote_type = emote_type
        self.emote_set_id = emote_set_id
