from dataclasses import dataclass


@dataclass
class CharityCampaignAmount:
    """
    Represents the amount of a donation in a charity campaign

    Attributes:
        value (int): The monetary amount
            The amount is specified in the currency’s minor unit
        decimal_places (int): The number of decimal places used by the currency
        currency (str): The ISO-4217 three-letter currency code that identifies the type of currency in value
    """

    value: int
    decimal_places: int
    currency: str
