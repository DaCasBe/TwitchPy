from .._utils import http
from ..dataclasses import Team, User


def get_channel_teams(token: str, client_id: str, broadcaster_id: str) -> list[dict]:
    url = "https://api.twitch.tv/helix/teams/channel"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {"broadcaster_id": broadcaster_id}

    return http.send_get(url, headers, params)


def get_teams(token: str, client_id: str, name: str = "", team_id: str = "") -> Team:
    url = "https://api.twitch.tv/helix/teams"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {}

    if name != "":
        params["name"] = name

    if team_id != "":
        params["id"] = team_id

    team = http.send_get(url, headers, params)[0]

    return Team(
        [
            User(user["user_id"], user["user_login"], user["user_name"])
            for user in team["users"]
        ],
        team["background_image_url"],
        team["banner"],
        team["created_at"],
        team["updated_at"],
        team["info"],
        team["thumbnail_url"],
        team["team_name"],
        team["team_display_name"],
        team["id"],
    )
