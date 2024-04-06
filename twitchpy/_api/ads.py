from .._utils import http

DEFAULT_TIMEOUT: int = 10


def start_commercial(
    token: str, client_id: str, broadcaster_id: int, length: int
) -> dict:
    url = "https://api.twitch.tv/helix/channels/commercial"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
        "Content-Type": "application/json",
    }
    payload = {"broadcaster_id": broadcaster_id, "length": length}

    return http.send_post_get_result(url, headers, payload)[0]


def get_ad_schedule(token: str, client_id: str, broadcaster_id: str) -> dict:
    url = "https://api.twitch.tv/helix/channels/ads"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {"broadcaster_id": broadcaster_id}

    return http.send_get(url, headers, params)[0]


def snooze_next_ad(token: str, client_id: str, broadcaster_id: str) -> dict:
    url = "https://api.twitch.tv/helix/channels/ads/schedule/snooze"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    payload = {"broadcaster_id": broadcaster_id}

    return http.send_post_get_result(url, headers, payload)[0]
