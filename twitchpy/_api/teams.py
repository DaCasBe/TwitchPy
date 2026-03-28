from datetime import datetime

from .._utils import date, http
from ..dataclasses import Team, User


class TeamsAPI:
    def __init__(self, access_token: str, client_id: str):
        self._access_token = access_token
        self._client_id = client_id

    async def get_channel_teams(self, broadcaster_id: str) -> list[Team]:
        url = "https://api.twitch.tv/helix/teams/channel"
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Client-Id": self._client_id,
        }
        params = {"broadcaster_id": broadcaster_id}

        teams = await http.send_get(url, headers, params)

        return [
            Team(
                [
                    User(
                        team["broadcaster_id"],
                        team["broadcaster_login"],
                        team["broadcaster_name"],
                    )
                ],
                team["background_image_url"],
                team["banner"],
                datetime.strptime(team["created_at"], date.RFC3339_FORMAT),
                datetime.strptime(team["updated_at"], date.RFC3339_FORMAT),
                team["info"],
                team["thumbnail_url"],
                team["team_name"],
                team["team_display_name"],
                team["id"],
            )
            for team in teams
        ]

    async def get_teams(
        self, name: str | None = None, team_id: str | None = None
    ) -> Team:
        url = "https://api.twitch.tv/helix/teams"
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Client-Id": self._client_id,
        }
        params = {}

        if name is not None:
            params["name"] = name

        if team_id is not None:
            params["id"] = team_id

        team = (await http.send_get(url, headers, params))[0]

        return Team(
            [
                User(user["user_id"], user["user_login"], user["user_name"])
                for user in team["users"]
            ],
            team["background_image_url"],
            team["banner"],
            datetime.strptime(team["created_at"], date.RFC3339_FORMAT),
            datetime.strptime(team["updated_at"], date.RFC3339_FORMAT),
            team["info"],
            team["thumbnail_url"],
            team["team_name"],
            team["team_display_name"],
            team["id"],
        )
