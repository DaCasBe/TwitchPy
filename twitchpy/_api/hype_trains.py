from datetime import datetime

from .._utils import date, http
from ..dataclasses import HypeTrainContribution, HypeTrainEvent, HypeTrainEventData


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
            HypeTrainEventData(
                event["event_data"]["broadcaster_id"],
                datetime.strptime(
                    event["event_data"]["cooldown_end_time"], date.RFC3339_FORMAT
                ),
                datetime.strptime(
                    event["event_data"]["expires_at"], date.RFC3339_FORMAT
                ),
                event["event_data"]["goal"],
                event["event_data"]["id"],
                HypeTrainContribution(
                    event["event_data"]["last_contribution"]["total"],
                    event["event_data"]["last_contribution"]["type"],
                    event["event_data"]["last_contribution"]["user"],
                ),
                event["event_data"]["level"],
                datetime.strptime(
                    event["event_data"]["started_at"], date.RFC3339_FORMAT
                ),
                [
                    HypeTrainContribution(
                        contribution["total"],
                        contribution["type"],
                        contribution["user"],
                    )
                    for contribution in event["event_data"]["top_contributions"]
                ],
                event["event_data"]["total"],
            ),
        )
        for event in events
    ]
