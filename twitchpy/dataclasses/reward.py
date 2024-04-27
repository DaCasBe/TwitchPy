from dataclasses import dataclass
from datetime import datetime

from ..dataclasses import Channel


@dataclass
class Reward:
    """
    Represents a reward

    Attributes:
        channel (Channel): The channel that owns the reward
        reward_id (str): ID of the reward
        title (str | None): The title of the reward
        prompt (str | None): The prompt for the viewer when they are redeeming the reward
        cost (int | None): The cost of the reward
        image (dict | None): Image of the reward
        default_image (dict | None): Default images of the reward
        background_color (str | None): Background color of the reward
        is_enabled (bool | None): Is the reward currently enabled
        is_user_input_required (bool | None): Does the user need to enter information when redeeming the reward
        max_per_stream_setting (tuple[bool, int]): Settings about maximum uses per stream
        max_per_user_per_stream_setting (tuple[bool, int]): Settings about maximum uses per stream and user
        global_cooldown_setting (tuple[bool, int]): Settings about global cooldown
        is_paused (bool | None): Is the reward currently paused
        is_in_stock (bool | None): Is the reward currently in stock
        should_redemptions_skip_request_queue (bool | None): Should redemptions be set to FULFILLED status immediately when redeemed and skip the request queue instead of the normal UNFULFILLED status
        redemptions_redeemed_current_stream (int | None): The number of redemptions redeemed during the current live stream
        cooldown_expires_at (datetime | None): Timestamp of the cooldown expiration
    """

    channel: Channel
    reward_id: str
    title: str | None = None
    prompt: str | None = None
    cost: int | None = None
    image: dict | None = None
    default_image: dict | None = None
    background_color: str | None = None
    is_enabled: bool | None = None
    is_user_input_required: bool | None = None
    max_per_stream_setting: tuple[bool, int] | None = None
    max_per_user_per_stream_setting: tuple[bool, int] | None = None
    global_cooldown_setting: tuple[bool, int] | None = None
    is_paused: bool | None = None
    is_in_stock: bool | None = None
    should_redemptions_skip_request_queue: bool | None = None
    redemptions_redeemed_current_stream: int | None = None
    cooldown_expires_at: datetime | None = None
