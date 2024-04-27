from dataclasses import dataclass


@dataclass
class BadgeVersion:
    """
    Represents a version of a chat badge

    Attributes:
        version_id (str): An ID that identifies this version of the badge
        image_url_1x (str): A URL to the small version (18px x 18px) of the badge
        image_url_2x (str): A URL to the medium version (36px x 36px) of the badge
        image_url_4x (str): A URL to the large version (72px x 72px) of the badge
        title (str): The title of the badge
        description (str): The description of the badge
        click_action (str): The action to take when clicking on the badge
        click_url (str): The URL to navigate to when clicking on the badge
    """

    version_id: str
    image_url_1x: str
    image_url_2x: str
    image_url_4x: str
    title: str
    description: str
    click_action: str
    click_url: str
