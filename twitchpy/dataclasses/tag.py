from dataclasses import dataclass


@dataclass
class Tag:
    """
    Represents a stream tag

    Attributes:
        tag_id (str): An ID that identifies the tag
        is_auto (bool): A Boolean value that determines whether the tag is an automatic tag
            You cannot add or remove automatic tags
            The value is true if the tag is an automatic tag; otherwise, false
        localization_names (dict): The localized names of the tag
        localization_descriptions (dict): The localized descriptions of the tag
    """

    tag_id: str
    is_auto: bool
    localization_names: dict
    localization_descriptions: dict
