from dataclasses import dataclass


@dataclass
class ContentClassificationLabel:
    """
    Represents a content classification label

    Attributes:
        label_id (str): Unique identifier for the label
        description (str): Localized description of the label
        name (str): Localized name of the label
    """

    label_id: str
    description: str
    name: str
