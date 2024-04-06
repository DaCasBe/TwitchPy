from .._utils import http
from ..dataclasses import Channel

ENDPOINT_VIPS = "https://api.twitch.tv/helix/channels/vips"


def get_channels(
    token: str, client_id: str, broadcaster_id: str | list[str]
) -> Channel | list[Channel]:
    url = "https://api.twitch.tv/helix/channels"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {"broadcaster_id": broadcaster_id}

    channels = http.send_get(url, headers, params)

    if len(channels) == 1:
        return Channel(
            channels[0]["broadcaster_id"],
            channels[0]["broadcaster_login"],
            channels[0]["broadcaster_name"],
            channels[0]["broadcaster_language"],
            channels[0]["game_name"],
            channels[0]["game_id"],
            channels[0]["title"],
            channels[0]["tags"],
            channels[0]["delay"],
            channels[0]["content_classification_labels"],
            channels[0]["is_branded_content"],
        )

    return [
        Channel(
            channel["broadcaster_id"],
            channel["broadcaster_login"],
            channel["broadcaster_name"],
            channel["broadcaster_language"],
            channel["game_name"],
            channel["game_id"],
            channel["title"],
            channel["tags"],
            channel["delay"],
            channel["content_classification_labels"],
            channel["is_branded_content"],
        )
        for channel in channels
    ]


def modify_channel_information(
    token: str,
    client_id: str,
    broadcaster_id: str,
    game_id: str | None = None,
    broadcaster_language: str | None = None,
    title: str | None = None,
    delay: int | None = None,
    tags: list[str] | None = None,
    content_classification_labels: list[dict] | None = None,
    is_branded_content: bool | None = None,
) -> None:
    url = "https://api.twitch.tv/helix/channels"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    data = {}
    data["broadcaster_id"] = broadcaster_id

    if game_id is not None:
        data["game_id"] = game_id

    if broadcaster_language is not None:
        data["broadcaster_language"] = broadcaster_language

    if title is not None:
        data["title"] = title

    if delay is not None:
        data["delay"] = delay

    if tags is not None and len(tags) > 0:
        data["tags"] = tags

    if (
        content_classification_labels is not None
        and len(content_classification_labels) > 0
    ):
        data["content_classification_labels"] = content_classification_labels

    if is_branded_content is not None:
        data["is_branded_content"] = is_branded_content

    http.send_patch(url, headers, data)


def get_channel_editors(token: str, client_id: str, broadcaster_id: str) -> list[dict]:
    url = "https://api.twitch.tv/helix/channels/editors"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {"broadcaster_id": broadcaster_id}

    return http.send_get(url, headers, params)


def get_followed_channels(
    token: str, client_id: str, user_id: str, broadcaster_id: str = "", first: int = 20
) -> list[dict]:
    url = "https://api.twitch.tv/helix/channels/followed"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {"user_id": user_id}

    if broadcaster_id != "":
        params["broadcaster_id"] = broadcaster_id

    return http.send_get_with_pagination(url, headers, params, first, 100)


def get_channel_followers(
    token: str, client_id: str, broadcaster_id: str, user_id: str = "", first: int = 20
) -> list[dict]:
    url = "https://api.twitch.tv/helix/channels/followers"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {"broadcaster_id": broadcaster_id}

    if user_id != "":
        params["user_id"] = user_id

    return http.send_get_with_pagination(url, headers, params, first, 100)


def get_vips(
    token: str,
    client_id: str,
    broadcaster_id: str,
    user_id: list[str] | None = None,
    first: int = 20,
) -> list[dict]:
    url = ENDPOINT_VIPS
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {}
    params["broadcaster_id"] = broadcaster_id

    if user_id is not None and len(user_id) > 0:
        params["user_id"] = user_id

    return http.send_get_with_pagination(url, headers, params, first, 20)


def add_channel_vip(
    token: str, client_id: str, user_id: str, broadcaster_id: str
) -> None:
    url = ENDPOINT_VIPS
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    payload = {"user_id": user_id, "broadcaster_id": broadcaster_id}

    http.send_post(url, headers, payload)


def remove_channel_vip(
    token: str, client_id: str, user_id: str, broadcaster_id: str
) -> None:
    url = ENDPOINT_VIPS
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    data = {"user_id": user_id, "broadcaster_id": broadcaster_id}

    http.send_delete(url, headers, data)
