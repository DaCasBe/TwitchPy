class Redemption:
    """
    Represents a reward redemption
    """

    def __init__(
        self,
        broadcaster_name,
        broadcaster_id,
        redemption_id,
        user_id,
        user_name,
        user_input,
        status,
        redeemed_at,
        reward,
    ):
        """
        Args:
            broadcaster_name (str): The display name of the broadcaster that the reward belongs to
            broadcaster_id (str): The id of the broadcaster that the reward belongs to
            redemption_id (str): The ID of the redemption
            user_id (str): The ID of the user that redeemed the reward
            user_name (str): The display name of the user that redeemed the reward
            user_input (str): The user input provided
            status (str): One of UNFULFILLED, FULFILLED or CANCELED
            redeemed_at (str): Timestamp of when the reward was redeemed
            reward (Reward): The custom reward that was redeemed at the time it was redeemed
        """

        self.broadcaster_name = broadcaster_name
        self.broadcaster_id = broadcaster_id
        self.id = redemption_id
        self.user_id = user_id
        self.user_name = user_name
        self.user_input = user_input
        self.status = status
        self.redeemed_at = redeemed_at
        self.reward = reward
