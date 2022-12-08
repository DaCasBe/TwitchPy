class Reward:
    """
    Represents a reward
    """
    
    def __init__(self, broadcaster_name, broadcaster_id, id, image="", background_color="", is_enabled=True, cost=0, title="", prompt="", is_user_input_required=False, max_per_stream_setting=None, max_per_user_per_stream_setting=None, global_cooldown_setting=None, is_paused=False, is_in_stock=True, default_image=None, should_redemptions_skip_request_queue=False, redemptions_redeemed_current_stream=0, cooldown_expires_at=None):
        """
        Args:
            broadcaster_name (str): Name of the channel owner of the reward
            broadcaster_id (str): ID of the channel owner of the reward
            id (str): ID of the reward
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

        self.broadcaster_name=broadcaster_name
        self.broadcaster_id=broadcaster_id
        self.id=id
        self.image=image
        self.background_color=background_color
        self.is_enabled=is_enabled
        self.cost=cost
        self.title=title
        self.prompt=prompt
        self.is_user_input_required=is_user_input_required

        if max_per_stream_setting is None:
            self.max_per_stream_setting = dict()

        if max_per_user_per_stream_setting is None:
            self.max_per_user_per_stream_setting = dict()

        if global_cooldown_setting is None:
            self.global_cooldown_setting = dict()

        self.is_paused=is_paused
        self.is_in_stock=is_in_stock

        if default_image is None:
            self.default_image = dict()

        self.should_redemptions_skip_request_queue=should_redemptions_skip_request_queue
        self.redemptions_redeemed_current_stream=redemptions_redeemed_current_stream
        self.cooldown_expires_at=cooldown_expires_at