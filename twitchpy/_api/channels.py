from datetime import datetime

from .._utils import date, http
from ..dataclasses import Channel, ContentClassificationLabel, Game, User

ENDPOINT_VIPS = "https://api.twitch.tv/helix/channels/vips"


def get_channel_information(
    token: str, client_id: str, broadcaster_id: list[str]
) -> list[Channel]:
    url = "https://api.twitch.tv/helix/channels"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {"broadcaster_id": broadcaster_id}

    channels = http.send_get(url, headers, params)

    return [
        Channel(
            User(
                channel["broadcaster_id"],
                channel["broadcaster_login"],
                channel["broadcaster_name"],
            ),
            channel["broadcaster_language"],
            Game(channel["game_id"], channel["game_name"]),
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
    content_classification_labels: list[ContentClassificationLabel] | None = None,
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


def get_channel_editors(token: str, client_id: str, broadcaster_id: str) -> list[User]:
    url = "https://api.twitch.tv/helix/channels/editors"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {"broadcaster_id": broadcaster_id}

    editors = http.send_get(url, headers, params)

    return [
        User(
            editor["user_id"],
            editor["user_name"].lower(),
            editor["user_name"],
            created_at=datetime.strptime(editor["created_at"], date.RFC3339_FORMAT),
        )
        for editor in editors
    ]


def get_followed_channels(
    token: str,
    client_id: str,
    user_id: str,
    broadcaster_id: str | None = None,
    first: int = 20,
) -> list[tuple[Channel, datetime]]:
    url = "https://api.twitch.tv/helix/channels/followed"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {"user_id": user_id}

    if broadcaster_id is not None:
        params["broadcaster_id"] = broadcaster_id

    followed_channels = http.send_get_with_pagination(url, headers, params, first, 100)

    return [
        (
            Channel(
                User(
                    followed_channel["broadcaster_id"],
                    followed_channel["broadcaster_login"],
                    followed_channel["broadcaster_name"],
                )
            ),
            datetime.strptime(followed_channel["followed_at"], date.RFC3339_FORMAT),
        )
        for followed_channel in followed_channels
    ]


def get_channel_followers(
    token: str,
    client_id: str,
    broadcaster_id: str,
    user_id: str | None = None,
    first: int = 20,
) -> list[tuple[Channel, datetime]]:
    url = "https://api.twitch.tv/helix/channels/followers"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {"broadcaster_id": broadcaster_id}

    if user_id is not None:
        params["user_id"] = user_id

    followers = http.send_get_with_pagination(url, headers, params, first, 100)

    return [
        (
            Channel(
                User(follower["user_id"], follower["user_login"], follower["user_name"])
            ),
            datetime.strptime(follower["followed_at"], date.RFC3339_FORMAT),
        )
        for follower in followers
    ]


def get_vips(
    token: str,
    client_id: str,
    broadcaster_id: str,
    user_id: list[str] | None = None,
    first: int = 20,
) -> list[User]:
    url = ENDPOINT_VIPS
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {}
    params["broadcaster_id"] = broadcaster_id

    if user_id is not None and len(user_id) > 0:
        params["user_id"] = user_id

    vips = http.send_get_with_pagination(url, headers, params, first, 20)

    return [User(vip["user_id"], vip["user_login"], vip["user_name"]) for vip in vips]


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
