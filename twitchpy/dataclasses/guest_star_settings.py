from dataclasses import dataclass


@dataclass
class GuestStarSettings:
    """
    Represents a Guest Star session's settings

    Attributes:
        is_moderator_send_live_enabled (bool): Flag determining if Guest Star moderators have access to control whether a guest is live once assigned to a slot
        slot_count (int): Number of slots the Guest Star call interface will allow the host to add to a call
        is_browser_source_audio_enabled (bool): Flag determining if Browser Sources subscribed to sessions on this channel should output audio
        group_layout (str): This setting determines how the guests within a session should be laid out within the browser source
            Possible values: TILED_LAYOUT, SCREENSHARE_LAYOUT
        browser_source_token (str): View only token to generate browser source URLs
    """

    is_moderator_send_live_enabled: bool
    slot_count: int
    is_browser_source_audio_enabled: bool
    group_layout: str
    browser_source_token: str
