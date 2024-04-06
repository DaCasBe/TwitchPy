from .._utils import http
from ..dataclasses import Game


def get_top_games(token: str, client_id: str, first: int = 20) -> list[Game]:
    url = "https://api.twitch.tv/helix/games/top"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }

    games = http.send_get_with_pagination(url, headers, {}, first, 100)

    return [
        Game(
            game["id"],
            game["name"],
            game["box_art_url"],
            game["igdb_id"],
        )
        for game in games
    ]


def get_games(
    token: str,
    client_id: str,
    game_id: list[str] | None = None,
    name: list[str] | None = None,
    igdb_id: list[str] | None = None,
) -> list[Game]:
    url = "https://api.twitch.tv/helix/games"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {}

    if game_id is not None and len(game_id) > 0:
        params["id"] = game_id

    if name is not None and len(name) > 0:
        params["name"] = name

    if igdb_id is not None and len(igdb_id) > 0:
        params["igdb_id"] = igdb_id

    games = http.send_get(url, headers, params)

    return [
        Game(game["id"], game["name"], game["box_art_url"], game["igdb_id"])
        for game in games
    ]
