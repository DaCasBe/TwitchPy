from .._utils import http


def get_creator_goals(token: str, client_id: str, broadcaster_id: str) -> list[dict]:
    url = "https://api.twitch.tv/helix/goals"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {"broadcaster_id": broadcaster_id}

    return http.send_get(url, headers, params)
