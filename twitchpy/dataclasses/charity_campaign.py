from dataclasses import dataclass

from ..dataclasses import Channel, CharityCampaignAmount


@dataclass
class CharityCampaign:
    """
    Represents a charity campaign

    Attributes:
        campaign_id (str): An ID that identifies the charity campaign
        channel (Channel): The channel that's running the campaign
        charity_name (str): The charity’s name
        charity_description (str): A description of the charity
        charity_logo (str): A URL to an image of the charity’s logo
        charity_website (str): A URL to the charity’s website
        current_amount (CharityCampaignAmount): The current amount of donations that the campaign has received
        target_amount (CharityCampaignAmount): The campaign’s fundraising goal
    """

    campaign_id: str
    channel: Channel
    charity_name: str
    charity_description: str
    charity_logo: str
    charity_website: str
    current_amount: CharityCampaignAmount
    target_amount: CharityCampaignAmount
