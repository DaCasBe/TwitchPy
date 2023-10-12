class CharityCampaignDonation:
    """
    Represents a donation made to a charity campaign
    """

    def __init__(
        self,
        id: str,
        campaign_id: str,
        user_id: str,
        user_login: str,
        user_name: str,
        amount: dict,
    ):
        """
        The function initializes an object with the given parameters.

        Args:
            id (str): An ID that identifies the donation
            campaign_id (str): An ID that identifies the charity campaign that the donation applies to
            user_id (str): An ID that identifies a user that donated money to the campaign
            user_login (str): The user’s login name
            user_name (str): The user’s display name
            amount (dict): The amount of money that the user donated
        used.
        """

        self.id = id
        self.campaign_id = campaign_id
        self.user_id = user_id
        self.user_login = user_login
        self.user_name = user_name
        self.amount = amount
