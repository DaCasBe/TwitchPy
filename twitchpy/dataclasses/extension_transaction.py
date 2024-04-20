from dataclasses import dataclass
from datetime import datetime

from ..dataclasses import Channel, Product, User


@dataclass
class ExtensionTransaction:
    """
    Represents an extension's transaction

    Attributes:
        transaction_id (str): An ID that identifies the transaction
        timestamp (datetime): The UTC date and time (in RFC3339 format) of the transaction
        channel (Channel): The channel where the transaction occurred
        user (User): The user that purchased the digital product
        product_type (str): The type of transaction
            Possible values: BITS_IN_EXTENSION
        product (Product): Contains details about the digital product
    """

    transaction_id: str
    timestamp: datetime
    channel: Channel
    user: User
    product_type: str
    product: Product
