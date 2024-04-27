from datetime import datetime

from .._utils import date, http
from ..dataclasses import Channel, CreatorGoal, User


def get_creator_goals(
    token: str, client_id: str, broadcaster_id: str
) -> list[CreatorGoal]:
    url = "https://api.twitch.tv/helix/goals"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {"broadcaster_id": broadcaster_id}

    goals = http.send_get(url, headers, params)

    return [
        CreatorGoal(
            goal["id"],
            Channel(
                User(
                    goal["broadcaster_id"],
                    goal["broadcaster_login"],
                    goal["broadcaster_name"],
                )
            ),
            goal["type"],
            goal["description"],
            goal["current_amount"],
            goal["target_amount"],
            datetime.strptime(goal["created_at"], date.RFC3339_FORMAT),
        )
        for goal in goals
    ]
