from .._utils import http
from ..dataclasses import Badge, Emote


def get_chatters(
    token: str, client_id: str, broadcaster_id: str, moderator_id: str, first: int = 100
) -> list[dict]:
    url = "https://api.twitch.tv/helix/chat/chatters"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {"broadcaster_id": broadcaster_id, "moderator_id": moderator_id}

    return http.send_get_with_pagination(url, headers, params, first, 100)


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
            emote["images"],
            emote["format"],
            emote["scale"],
            emote["theme_mode"],
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
            emote["images"],
            emote["format"],
            emote["scale"],
            emote["theme_mode"],
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
            emote["images"],
            emote["format"],
            emote["scale"],
            emote["theme_mode"],
            emote_type=emote["emote_type"],
            emote_set_id=emote["emote_set_id"],
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

    return [Badge(badge["set_id"], badge["versions"]) for badge in badges]


def get_global_chat_badges(token: str, client_id: str) -> list[Badge]:
    url = "https://api.twitch.tv/helix/chat/badges/global"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }

    badges = http.send_get(url, headers, {})

    return [Badge(badge["set_id"], badge["versions"]) for badge in badges]


def get_chat_settings(
    token: str, client_id: str, broadcaster_id: str, moderator_id: str = ""
) -> dict:
    url = "https://api.twitch.tv/helix/chat/settings"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {"broadcaster_id": broadcaster_id, "moderator_id": moderator_id}

    return http.send_get(url, headers, params)[0]


def update_chat_settings(
    token: str,
    client_id: str,
    broadcaster_id: str,
    moderator_id: str,
    emote_mode: bool | None = None,
    follower_mode: bool | None = None,
    follower_mode_duration: int = 0,
    non_moderator_chat_delay: bool | None = None,
    non_moderator_chat_delay_duration: int = 0,
    slow_mode: bool | None = None,
    slow_mode_wait_time: int = 30,
    subscriber_mode: bool | None = None,
    unique_chat_mode: bool | None = None,
) -> dict:
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

    if follower_mode_duration != 0:
        data["follower_mode_duration"] = follower_mode_duration

    if non_moderator_chat_delay is not None:
        data["non_moderator_chat_delay"] = non_moderator_chat_delay

    if non_moderator_chat_delay_duration != 0:
        data["non_moderator_chat_delay_duration"] = non_moderator_chat_delay_duration

    if slow_mode is not None:
        data["slow_mode"] = slow_mode

    if slow_mode_wait_time != 30:
        data["slow_mode_wait_time"] = slow_mode_wait_time

    if subscriber_mode is not None:
        data["subscriber_mode"] = subscriber_mode

    if unique_chat_mode is not None:
        data["unique_chat_mode"] = unique_chat_mode

    return http.send_patch_get_result(url, headers, data)[0]


def send_chat_announcement(
    token: str,
    client_id: str,
    broadcaster_id: str,
    moderator_id: str,
    message: str,
    color: str = "",
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

    if color != "":
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
    reply_parent_message_id: str = "",
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

    if reply_parent_message_id != "":
        payload["reply_parent_message_id"] = reply_parent_message_id

    return http.send_post_get_result(url, headers, payload)[0]


def get_user_chat_color(
    token: str, client_id: str, user_id: str | list[str]
) -> dict | list[dict]:
    url = "https://api.twitch.tv/helix/chat/color"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {"user_id": user_id}

    color_settings = http.send_get(url, headers, params)

    if len(color_settings) == 1:
        return color_settings[0]

    return color_settings


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
