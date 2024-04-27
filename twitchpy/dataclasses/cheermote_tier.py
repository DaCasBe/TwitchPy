from dataclasses import dataclass


@dataclass
class CheermoteTier:
    """
    Represents a tier level that a Cheermote supports

    Attributes:
        min_bits (int): The minimum number of Bits that you must cheer at this tier level
            The maximum number of Bits that you can cheer at this level is determined by the required minimum Bits of the next tier level minus 1
            The minimum Bits value of the last tier is the maximum number of Bits you can cheer using this Cheermote
        tier_id (str): The tier level
            Possible values: 1, 100, 500, 1000, 5000, 10000, 100000
        color (str): The hex code of the color associated with this tier level
        images (dict): The animated and static image sets for the Cheermote
            The dictionary of images is organized by theme, format, and size
            The theme keys are dark and light
            Each theme is a dictionary of formats: animated and static
            Each format is a dictionary of sizes: 1, 1.5, 2, 3, and 4
            The value of each size contains the URL to the image
        can_cheer (bool): A Boolean value that determines whether users can cheer at this tier level
        show_in_bits_card (bool): A Boolean value that determines whether this tier level is shown in the Bits card
    """

    min_bits: int
    tier_id: str
    color: str
    images: dict
    can_cheer: bool
    show_in_bits_card: bool
