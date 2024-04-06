from .._utils import http
from ..dataclasses import HypeTrainEvent


def get_hype_train_events(
    token: str, client_id: str, broadcaster_id: str, first: int = 1
) -> list[HypeTrainEvent]:
    url = "https://api.twitch.tv/helix/hypetrain/events"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {"broadcaster_id": broadcaster_id}

    events = http.send_get_with_pagination(url, headers, params, first, 100)

    return [
        HypeTrainEvent(
            event["id"],
            event["event_type"],
            event["event_timestamp"],
            event["version"],
            event["event_data"],
        )
        for event in events
    ]
