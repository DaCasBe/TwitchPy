from dataclasses import dataclass


@dataclass
class ProductCost:
    """
    Represents a digital product's cost

    Attributes:
        amount (int): The amount exchanged for the digital product
        type (str): The type of currency exchanged
            Possible values: bits
    """

    amount: int
    type: str
