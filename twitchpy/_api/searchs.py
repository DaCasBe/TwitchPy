from .._utils import http
from ..dataclasses import Channel, Game, User


def search_categories(
    token: str, client_id: str, query: str, first: int = 20
) -> list[Game]:
    url = "https://api.twitch.tv/helix/search/categories"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {"query": query}

    games = http.send_get_with_pagination(url, headers, params, first, 100)

    return [Game(game["id"], game["name"], game["box_art_url"]) for game in games]


def search_channels(
    token: str, client_id: str, query: str, first: int = 20, live_only: bool = False
) -> list[Channel]:
    url = "https://api.twitch.tv/helix/search/channels"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {"query": query, "live_only": live_only}

    channels = http.send_get_with_pagination(url, headers, params, first, 100)

    return [
        Channel(
            User(channel["id"], channel["broadcaster_login"], channel["display_name"]),
            channel["broadcaster_language"],
            Game(channel["game_id"], channel["game_name"]),
            channel["title"],
            channel["tags"],
        )
        for channel in channels
    ]
