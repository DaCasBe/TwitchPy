from datetime import datetime

from .._utils import date, http
from ..dataclasses import AdSchedule, Commercial


class AdsAPI:
    def __init__(self, access_token: str, client_id: str):
        self._access_token = access_token
        self._client_id = client_id

    async def start_commercial(self, broadcaster_id: int, length: int) -> Commercial:
        url = "https://api.twitch.tv/helix/channels/commercial"
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Client-Id": self._client_id,
            "Content-Type": "application/json",
        }
        payload = {"broadcaster_id": broadcaster_id, "length": length}

        commercial = (await http.send_post_get_result(url, headers, payload))[0]

        return Commercial(
            commercial["length"], commercial["message"], commercial["retry_after"]
        )

    async def get_ad_schedule(self, broadcaster_id: str) -> AdSchedule:
        url = "https://api.twitch.tv/helix/channels/ads"
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Client-Id": self._client_id,
        }
        params = {"broadcaster_id": broadcaster_id}

        ad_schedule = (await http.send_get(url, headers, params))[0]

        return AdSchedule(
            ad_schedule["snooze_count"],
            datetime.fromtimestamp(ad_schedule["snooze_refresh_at"]),
            datetime.fromtimestamp(ad_schedule["next_ad_at"]),
            ad_schedule["duration"],
            datetime.fromtimestamp(ad_schedule["last_ad_at"]),
            ad_schedule["preroll_free_time"],
        )

    async def snooze_next_ad(self, broadcaster_id: str) -> AdSchedule:
        url = "https://api.twitch.tv/helix/channels/ads/schedule/snooze"
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Client-Id": self._client_id,
        }
        payload = {"broadcaster_id": broadcaster_id}

        ad_schedule = (await http.send_post_get_result(url, headers, payload))[0]

        return AdSchedule(
            ad_schedule["snooze_count"],
            datetime.strptime(ad_schedule["snooze_refresh_at"], date.RFC3339_FORMAT),
            datetime.strptime(ad_schedule["next_ad_at"], date.RFC3339_FORMAT),
        )
