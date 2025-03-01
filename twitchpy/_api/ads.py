from datetime import datetime

from .._utils import date, http
from ..dataclasses import AdSchedule, Commercial


def start_commercial(
    token: str, client_id: str, broadcaster_id: int, length: int
) -> Commercial:
    url = "https://api.twitch.tv/helix/channels/commercial"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
        "Content-Type": "application/json",
    }
    payload = {"broadcaster_id": broadcaster_id, "length": length}

    commercial = http.send_post_get_result(url, headers, payload)[0]

    return Commercial(
        commercial["length"], commercial["message"], commercial["retry_after"]
    )


def get_ad_schedule(token: str, client_id: str, broadcaster_id: str) -> AdSchedule:
    url = "https://api.twitch.tv/helix/channels/ads"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {"broadcaster_id": broadcaster_id}

    ad_schedule = http.send_get(url, headers, params)[0]

    return AdSchedule(
        ad_schedule["snooze_count"],
        datetime.fromtimestamp(ad_schedule["snooze_refresh_at"]),
        datetime.fromtimestamp(ad_schedule["next_ad_at"]),
        ad_schedule["duration"],
        datetime.fromtimestamp(ad_schedule["last_ad_at"]),
        ad_schedule["preroll_free_time"],
    )


def snooze_next_ad(token: str, client_id: str, broadcaster_id: str) -> AdSchedule:
    url = "https://api.twitch.tv/helix/channels/ads/schedule/snooze"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    payload = {"broadcaster_id": broadcaster_id}

    ad_schedule = http.send_post_get_result(url, headers, payload)[0]

    return AdSchedule(
        ad_schedule["snooze_count"],
        datetime.strptime(ad_schedule["snooze_refresh_at"], date.RFC3339_FORMAT),
        datetime.strptime(ad_schedule["next_ad_at"], date.RFC3339_FORMAT),
    )
