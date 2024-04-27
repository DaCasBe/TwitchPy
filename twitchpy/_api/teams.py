from datetime import datetime

from .._utils import date, http
from ..dataclasses import Team, User


def get_channel_teams(token: str, client_id: str, broadcaster_id: str) -> list[Team]:
    url = "https://api.twitch.tv/helix/teams/channel"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {"broadcaster_id": broadcaster_id}

    teams = http.send_get(url, headers, params)

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


def get_teams(
    token: str, client_id: str, name: str | None = None, team_id: str | None = None
) -> Team:
    url = "https://api.twitch.tv/helix/teams"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {}

    if name is not None:
        params["name"] = name

    if team_id is not None:
        params["id"] = team_id

    team = http.send_get(url, headers, params)[0]

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
