from dataclasses import dataclass
from datetime import datetime

from ..dataclasses import CheermoteTier


@dataclass
class Cheermote:
    """
    Represents a Cheermote

    Attributes:
        prefix (str): The name portion of the Cheermote string that you use in chat to cheer Bits
            The full Cheermote string is the concatenation of {prefix} + {number of Bits}
        tiers (list[CheermoteTier]): A list of tier levels that the Cheermote supports
            Each tier identifies the range of Bits that you can cheer at that tier level and an image that graphically identifies the tier level
        type (str): The type of Cheermote
            Possible values: global_first_party, global_third_party, channel_custom, display_only, sponsored
        order (int): The order that the Cheermotes are shown in the Bits card
        last_updated (datetime): The date and time, in RFC3339 format, when this Cheermote was last updated
        is_charitable (bool): A Boolean value that indicates whether this Cheermote provides a charitable contribution match during charity campaigns
    """

    prefix: str
    tiers: list[CheermoteTier]
    type: str
    order: int
    last_updated: datetime
    is_charitable: bool
