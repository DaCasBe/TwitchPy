from datetime import datetime

from .._utils import date, http
from ..dataclasses import Channel, CreatorGoal, User


class GoalsAPI:
    def __init__(self, access_token: str, client_id: str):
        self._access_token = access_token
        self._client_id = client_id

    async def get_creator_goals(self, broadcaster_id: str) -> list[CreatorGoal]:
        url = "https://api.twitch.tv/helix/goals"
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Client-Id": self._client_id,
        }
        params = {"broadcaster_id": broadcaster_id}

        goals = await http.send_get(url, headers, params)

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
