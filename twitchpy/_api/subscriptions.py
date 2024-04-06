from .._utils import http


def get_broadcaster_subscriptions(
    token: str,
    client_id: str,
    broadcaster_id: str,
    user_id: list[str] | None = None,
    first: int = 20,
) -> list[dict]:
    url = "https://api.twitch.tv/helix/subscriptions"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {}
    params["broadcaster_id"] = broadcaster_id

    if user_id is not None and len(user_id) > 0:
        params["user_id"] = user_id

    if first != 20:
        params["first"] = first

    return http.send_get_with_pagination(url, headers, params, first, 100)


def check_user_subscription(
    token: str, client_id: str, broadcaster_id: str, user_id: str
) -> dict:
    url = "https://api.twitch.tv/helix/subscriptions/user"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {"broadcaster_id": broadcaster_id, "user_id": user_id}

    return http.send_get(url, headers, params)[0]
