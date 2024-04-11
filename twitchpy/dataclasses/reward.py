from dataclasses import dataclass


@dataclass
class Reward:
    """
    Represents a reward

    Attributes:
        broadcaster_name (str): Name of the channel owner of the reward
        broadcaster_id (str): ID of the channel owner of the reward
        reward_id (str): ID of the reward
        image (str): Image of the reward
        background_color (str): Background color of the reward
        is_enabled (bool): Is the reward currently enabled
        cost (int): The cost of the reward
        title (str): The title of the reward
        prompt (str): The prompt for the viewer when they are redeeming the reward
        is_user_input_required (bool): Does the user need to enter information when redeeming the reward
        max_per_stream_setting (dict): Settings about maximum uses per stream
        max_per_user_per_stream_setting (dict): Settings about maximum uses per stream and user
        global_cooldown_setting (dict): Settings about global cooldown
        is_paused (bool): Is the reward currently paused
        is_in_stock (bool): Is the reward currently in stock
        default_image (dict): Default images of the reward
        should_redemptions_skip_request_queue (bool): Should redemptions be set to FULFILLED status immediately when redeemed and skip the request queue instead of the normal UNFULFILLED status
        redemptions_redeemed_current_stream (int): The number of redemptions redeemed during the current live stream
        cooldown_expires_at (int): Timestamp of the cooldown expiration
    """

    broadcaster_name: str
    broadcaster_id: str
    reward_id: str
    image: str = ""
    background_color: str = ""
    is_enabled: bool = True
    cost: int = 0
    title: str = ""
    prompt: str = ""
    is_user_input_required: bool = False
    max_per_stream_setting: dict | None = None
    max_per_user_per_stream_setting: dict | None = None
    global_cooldown_setting: dict | None = None
    is_paused: bool = False
    is_in_stock: bool = True
    default_image: dict | None = None
    should_redemptions_skip_request_queue: bool = False
    redemptions_redeemed_current_stream: int = 0
    cooldown_expires_at: int | None = None
