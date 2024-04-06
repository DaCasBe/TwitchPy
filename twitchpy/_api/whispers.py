from .._utils import http


def send_whisper(
    token: str, client_id: str, from_user_id: str, to_user_id: str, message: str
) -> None:
    url = "https://api.twitch.tv/helix/whispers"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
        "Content-Type": "application/json",
    }
    payload = {
        "from_user_id": from_user_id,
        "to_user_id": to_user_id,
        "message": message,
    }

    http.send_post(url, headers, payload)
