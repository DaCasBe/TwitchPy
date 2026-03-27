from datetime import datetime

from .._utils import date, http


async def start_raid(
    token: str, client_id: str, from_broadcaster_id: str, to_broadcaster_id: str
) -> tuple[datetime, bool]:
    url = "https://api.twitch.tv/helix/raids"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    payload = {
        "from_broadcaster_id": from_broadcaster_id,
        "to_broadcaster_id": to_broadcaster_id,
    }

    raid = (await http.send_post_get_result(url, headers, payload))[0]

    return (
        datetime.strptime(raid["created_at"], date.RFC3339_FORMAT),
        raid["is_mature"],
    )


async def cancel_raid(token: str, client_id: str, broadcaster_id: str) -> None:
    url = "https://api.twitch.tv/helix/raids"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    data = {"broadcaster_id": broadcaster_id}

    await http.send_delete(url, headers, data)
