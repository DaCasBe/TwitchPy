from dataclasses import dataclass

from ..dataclasses import CharityCampaignAmount, User


@dataclass
class CharityCampaignDonation:
    """
    Represents a donation made to a charity campaign

    Attributes:
        donation_id (str): An ID that identifies the donation
        campaign_id (str): An ID that identifies the charity campaign that the donation applies to
        user (User): The user that donated money to the campaign
        amount (CharityCampaignAmount): The amount of money that the user donated
    """

    donation_id: str
    campaign_id: str
    user: User
    amount: CharityCampaignAmount
