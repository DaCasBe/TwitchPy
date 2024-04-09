from .._utils import http
from ..dataclasses import User

ENDPOINT_BLOCKS = "https://api.twitch.tv/helix/users/blocks"


def get_users(
    token: str,
    client_id: str,
    user_ids: list[str] | None = None,
    login: list[str] | None = None,
) -> list[User]:
    url = "https://api.twitch.tv/helix/users"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {}

    if user_ids is not None and len(user_ids) > 0:
        params["id"] = user_ids

    if login is not None and len(login) > 0:
        params["login"] = [user_login.replace("@", "").lower() for user_login in login]

    users = http.send_get(url, headers, params)

    return [
        User(
            user["id"],
            user["login"],
            user["display_name"],
            user["type"],
            user["broadcaster_type"],
            user["description"],
            user["profile_image_url"],
            user["offline_image_url"],
            user["view_count"],
        )
        for user in users
    ]


def update_user(token: str, client_id: str, description: str = "") -> User:
    url = "https://api.twitch.tv/helix/users"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    data = {}

    if description != "":
        data = {"description": description}

    user = http.send_put_get_result(url, headers, data)[0]

    return User(
        user["id"],
        user["login"],
        user["display_name"],
        user["type"],
        user["broadcaster_type"],
        user["description"],
        user["profile_image_url"],
        user["offline_image_url"],
        user["view_count"],
    )


def get_user_block_list(
    token: str, client_id: str, broadcaster_id: str, first: int = 20
) -> list[dict]:
    url = ENDPOINT_BLOCKS
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {}
    params["broadcaster_id"] = broadcaster_id

    if first != 20:
        params["first"] = first

    return http.send_get_with_pagination(url, headers, params, first, 100)


def block_user(
    token: str,
    client_id: str,
    target_user_id: str,
    source_context: str = "",
    reason: str = "",
) -> None:
    url = ENDPOINT_BLOCKS
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    data = {"target_user_id": target_user_id}

    if source_context != "":
        data["source_context"] = source_context

    if reason != "":
        data["reason"] = reason

    http.send_put(url, headers, data)


def unblock_user(token: str, client_id: str, target_user_id: str) -> None:
    url = ENDPOINT_BLOCKS
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    data = {"target_user_id": target_user_id}

    http.send_delete(url, headers, data)


def get_user_extensions(token: str, client_id: str) -> list[dict]:
    url = "https://api.twitch.tv/helix/users/extensions/list"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }

    return http.send_get(url, headers, {})


def get_user_active_extensions(
    token: str, client_id: str, user_id: str = ""
) -> list[dict]:
    url = "https://api.twitch.tv/helix/users/extensions"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {}

    if user_id != "":
        params = {"user_id": user_id}

    return http.send_get(url, headers, params)


def update_user_extensions(token: str, client_id: str) -> list[dict]:
    url = "https://api.twitch.tv/helix/users/extensions"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
        "Content-Type": "application/json",
    }

    return http.send_put_get_result(url, headers, {})