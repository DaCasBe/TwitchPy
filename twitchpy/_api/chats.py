from .._utils import http
from ..dataclasses import Badge, BadgeVersion, ChatSettings, Emote, User


def get_chatters(
    token: str, client_id: str, broadcaster_id: str, moderator_id: str, first: int = 100
) -> list[User]:
    url = "https://api.twitch.tv/helix/chat/chatters"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {"broadcaster_id": broadcaster_id, "moderator_id": moderator_id}

    chatters = http.send_get_with_pagination(url, headers, params, first, 100)

    return [
        User(chatter["user_id"], chatter["user_login"], chatter["user_name"])
        for chatter in chatters
    ]


def get_channel_emotes(token: str, client_id: str, broadcaster_id: str) -> list[Emote]:
    url = "https://api.twitch.tv/helix/chat/emotes"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {"broadcaster_id": broadcaster_id}

    emotes = http.send_get(url, headers, params)

    return [
        Emote(
            emote["id"],
            emote["name"],
            emote["format"],
            emote["scale"],
            emote["theme_mode"],
            emote["images"],
            emote["tier"],
            emote["emote_type"],
            emote["emote_set_id"],
        )
        for emote in emotes
    ]


def get_global_emotes(token: str, client_id: str) -> list[Emote]:
    url = "https://api.twitch.tv/helix/chat/emotes/global"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }

    emotes = http.send_get(url, headers, {})

    return [
        Emote(
            emote["id"],
            emote["name"],
            emote["format"],
            emote["scale"],
            emote["theme_mode"],
            emote["images"],
        )
        for emote in emotes
    ]


def get_emote_sets(token: str, client_id: str, emote_set_id: list[str]) -> list[Emote]:
    url = "https://api.twitch.tv/helix/chat/emotes/set"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {"emote_set_id": emote_set_id}

    emotes = http.send_get(url, headers, params)

    return [
        Emote(
            emote["id"],
            emote["name"],
            emote["format"],
            emote["scale"],
            emote["theme_mode"],
            emote["images"],
            emote_type=emote["emote_type"],
            emote_set_id=emote["emote_set_id"],
            owner_id=emote["owner_id"],
        )
        for emote in emotes
    ]


def get_channel_chat_badges(
    token: str, client_id: str, broadcaster_id: str
) -> list[Badge]:
    url = "https://api.twitch.tv/helix/chat/badges"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {"broadcaster_id": broadcaster_id}

    badges = http.send_get(url, headers, params)

    return [
        Badge(
            badge["set_id"],
            [
                BadgeVersion(
                    version["id"],
                    version["image_url_1x"],
                    version["image_url_2x"],
                    version["image_url_4x"],
                    version["title"],
                    version["description"],
                    version["click_action"],
                    version["click_url"],
                )
                for version in badge["versions"]
            ],
        )
        for badge in badges
    ]


def get_global_chat_badges(token: str, client_id: str) -> list[Badge]:
    url = "https://api.twitch.tv/helix/chat/badges/global"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }

    badges = http.send_get(url, headers, {})

    return [
        Badge(
            badge["set_id"],
            [
                BadgeVersion(
                    version["id"],
                    version["image_url_1x"],
                    version["image_url_2x"],
                    version["image_url_4x"],
                    version["title"],
                    version["description"],
                    version["click_action"],
                    version["click_url"],
                )
                for version in badge["versions"]
            ],
        )
        for badge in badges
    ]


def get_chat_settings(
    token: str, client_id: str, broadcaster_id: str, moderator_id: str | None = None
) -> ChatSettings:
    url = "https://api.twitch.tv/helix/chat/settings"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {"broadcaster_id": broadcaster_id}

    if moderator_id is not None:
        params["moderator_id"] = moderator_id

    settings = http.send_get(url, headers, params)[0]

    return ChatSettings(
        settings["broadcaster_id"],
        settings["emote_mode"],
        settings["follower_mode"],
        settings["follower_mode_duration"],
        settings["moderator_id"],
        settings["non_moderator_chat_delay"],
        settings["non_moderator_chat_delay_duration"],
        settings["slow_mode"],
        settings["slow_mode_wait_time"],
        settings["subscriber_mode"],
        settings["unique_chat_mode"],
    )


def get_user_emotes(
    token: str, client_id: str, user_id: str, broadcaster_id: str | None = None
) -> list[Emote]:
    url = "https://api.twitch.tv/helix/chat/emotes/user"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {"user_id": user_id}

    if broadcaster_id is not None:
        params["broadcaster_id"] = broadcaster_id

    emotes = http.send_get_with_infinite_pagination(url, headers, params)

    return [
        Emote(
            emote["id"],
            emote["name"],
            emote["format"],
            emote["scale"],
            emote["theme_mode"],
            emote_type=emote["emote_type"],
            emote_set_id=emote["emote_set_id"],
            owner_id=emote["owner_id"],
        )
        for emote in emotes
    ]


def update_chat_settings(
    token: str,
    client_id: str,
    broadcaster_id: str,
    moderator_id: str,
    emote_mode: bool | None = None,
    follower_mode: bool | None = None,
    follower_mode_duration: int | None = None,
    non_moderator_chat_delay: bool | None = None,
    non_moderator_chat_delay_duration: int | None = None,
    slow_mode: bool | None = None,
    slow_mode_wait_time: int | None = None,
    subscriber_mode: bool | None = None,
    unique_chat_mode: bool | None = None,
) -> ChatSettings:
    url = "https://api.twitch.tv/helix/chat/settings"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    data = {}
    data["broadcaster_id"] = broadcaster_id
    data["moderator_id"] = moderator_id

    if emote_mode is not None:
        data["emote_mode"] = emote_mode

    if follower_mode is not None:
        data["follower_mode"] = follower_mode

    if follower_mode_duration is not None:
        data["follower_mode_duration"] = follower_mode_duration

    if non_moderator_chat_delay is not None:
        data["non_moderator_chat_delay"] = non_moderator_chat_delay

    if non_moderator_chat_delay_duration is not None:
        data["non_moderator_chat_delay_duration"] = non_moderator_chat_delay_duration

    if slow_mode is not None:
        data["slow_mode"] = slow_mode

    if slow_mode_wait_time is not None:
        data["slow_mode_wait_time"] = slow_mode_wait_time

    if subscriber_mode is not None:
        data["subscriber_mode"] = subscriber_mode

    if unique_chat_mode is not None:
        data["unique_chat_mode"] = unique_chat_mode

    settings = http.send_patch_get_result(url, headers, data)[0]

    return ChatSettings(
        settings["broadcaster_id"],
        settings["emote_mode"],
        settings["follower_mode"],
        settings["follower_mode_duration"],
        settings["moderator_id"],
        settings["non_moderator_chat_delay"],
        settings["non_moderator_chat_delay_duration"],
        settings["slow_mode"],
        settings["slow_mode_wait_time"],
        settings["subscriber_mode"],
        settings["unique_chat_mode"],
    )


def send_chat_announcement(
    token: str,
    client_id: str,
    broadcaster_id: str,
    moderator_id: str,
    message: str,
    color: str | None = None,
) -> None:

    url = "https://api.twitch.tv/helix/chat/announcements"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
        "Content-Type": "application/json",
    }
    payload = {
        "broadcaster_id": broadcaster_id,
        "moderator_id": moderator_id,
        "message": message,
    }

    if color is not None:
        payload["color"] = color

    http.send_post(url, headers, payload)


def send_a_shoutout(
    token: str,
    client_id: str,
    from_broadcaster_id: str,
    to_broadcaster_id: str,
    moderator_id: str,
) -> None:
    url = "https://api.twitch.tv/helix/chat/shoutouts"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    payload = {
        "from_broadcaster_id": from_broadcaster_id,
        "to_broadcaster_id": to_broadcaster_id,
        "moderator_id": moderator_id,
    }

    http.send_post(url, headers, payload)


def send_chat_message(
    token: str,
    client_id: str,
    broadcaster_id: str,
    sender_id: str,
    message: str,
    reply_parent_message_id: str | None = None,
) -> dict:
    url = "https://api.twitch.tv/helix/chat/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
        "Content-Type": "application/json",
    }
    payload = {
        "broadcaster_id": broadcaster_id,
        "sender_id": sender_id,
        "message": message,
    }

    if reply_parent_message_id is not None:
        payload["reply_parent_message_id"] = reply_parent_message_id

    return http.send_post_get_result(url, headers, payload)[0]


def get_user_chat_color(
    token: str, client_id: str, user_id: list[str]
) -> list[tuple[User, str]]:
    url = "https://api.twitch.tv/helix/chat/color"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {"user_id": user_id}

    color_settings = http.send_get(url, headers, params)

    return [
        (
            User(setting["user_id"], setting["user_login"], setting["user_name"]),
            setting["color"],
        )
        for setting in color_settings
    ]


def update_user_chat_color(
    token: str, client_id: str, user_id: str, color: str
) -> None:
    url = "https://api.twitch.tv/helix/chat/color"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    data = {"user_id": user_id, "color": color}

    http.send_put(url, headers, data)
