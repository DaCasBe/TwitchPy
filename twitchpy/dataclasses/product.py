from dataclasses import dataclass

from ..dataclasses import ProductCost


@dataclass
class Product:
    """
    Represents a digital product

    Attributes:
        sku (str): An ID that identifies the digital product
        cost (ProductCost): The digital product’s cost
        in_development (bool): A Boolean value that determines whether the product is in development
        display_name (str): The name of the digital product
        expiration (str): This field is always empty since you may purchase only unexpired products
        broadcast (bool): A Boolean value that determines whether the data was broadcast to all instances of the extension
        domain (str | None): The product's domain
    """

    sku: str
    cost: ProductCost
    in_development: bool
    display_name: str
    expiration: str
    broadcast: bool
    domain: str | None = None
