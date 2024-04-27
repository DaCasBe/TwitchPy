from dataclasses import dataclass


@dataclass
class HypeTrainContribution:
    """
    Represents a contribution to a Hype Train's goal

    Attributes:
        total (int): The total amount contributed
        type (str): The contribution method used
            Possible values: BITS SUBS OTHER
        user (str): The ID of the user that made the contribution
    """

    total: int
    type: str
    user: str
