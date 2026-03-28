from datetime import datetime

from .._utils import date, http


class RaidsAPI:
    def __init__(self, access_token: str, client_id: str):
        self._access_token = access_token
        self._client_id = client_id

    async def start_raid(
        self, from_broadcaster_id: str, to_broadcaster_id: str
    ) -> tuple[datetime, bool]:
        url = "https://api.twitch.tv/helix/raids"
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Client-Id": self._client_id,
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

    async def cancel_raid(self, broadcaster_id: str) -> None:
        url = "https://api.twitch.tv/helix/raids"
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Client-Id": self._client_id,
        }
        data = {"broadcaster_id": broadcaster_id}

        await http.send_delete(url, headers, data)
