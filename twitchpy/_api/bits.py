from .._utils import http


def get_bits_leaderboard(
    token: str,
    client_id: str,
    count: int = 10,
    period: str = "all",
    started_at: str = "",
    user_id: str = "",
) -> list[dict]:
    url = "https://api.twitch.tv/helix/bits/leaderboard"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {}

    if count != 10:
        params["count"] = count

    if period != "all":
        params["period"] = period

    if started_at != "":
        params["started_at"] = started_at

    if user_id != "":
        params["user_id"] = user_id

    return http.send_get(url, headers, params)


def get_cheermotes(token: str, client_id: str, broadcaster_id: str = "") -> list[dict]:
    url = "https://api.twitch.tv/helix/bits/cheermotes"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {}

    if broadcaster_id != "":
        params = {"broadcaster_id": broadcaster_id}

    return http.send_get(url, headers, params)
