from .._utils import http


def start_raid(
    token: str, client_id: str, from_broadcaster_id: str, to_broadcaster_id: str
) -> dict:
    url = "https://api.twitch.tv/helix/raids"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    payload = {
        "from_broadcaster_id": from_broadcaster_id,
        "to_broadcaster_id": to_broadcaster_id,
    }

    return http.send_post_get_result(url, headers, payload)[0]


def cancel_raid(token: str, client_id: str, broadcaster_id: str) -> None:
    url = "https://api.twitch.tv/helix/raids"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    data = {"broadcaster_id": broadcaster_id}

    http.send_delete(url, headers, data)
