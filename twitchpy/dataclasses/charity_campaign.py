from dataclasses import dataclass


@dataclass
class CharityCampaign:
    """
    Represents a charity campaign

    Attributes:
        campaign_id (str): An ID that identifies the charity campaign
        broadcaster_id (str): An ID that identifies the broadcaster that’s running the campaign
        broadcaster_name (str): The broadcaster’s display name
        broadcaster_login (str): The broadcaster’s login name
        charity_name (str): The charity’s name
        charity_description (str): A description of the charity
        charity_logo (str): A URL to an image of the charity’s logo
        charity_website (str): A URL to the charity’s website
        current_amount (dict): The current amount of donations that the campaign has received
        target_amount (dict): The campaign’s fundraising goal
    """

    campaign_id: str
    broadcaster_id: str
    broadcaster_name: str
    broadcaster_login: str
    charity_name: str
    charity_description: str
    charity_logo: str
    charity_website: str
    current_amount: dict
    target_amount: dict
