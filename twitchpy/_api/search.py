from .._utils import http
from ..dataclasses import Channel, Game, User


class SearchAPI:
    def __init__(self, access_token: str, client_id: str):
        self._access_token = access_token
        self._client_id = client_id

    async def search_categories(self, query: str, first: int = 20) -> list[Game]:
        url = "https://api.twitch.tv/helix/search/categories"
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Client-Id": self._client_id,
        }
        params = {"query": query}

        games = await http.send_get_with_pagination(url, headers, params, first, 100)

        return [Game(game["id"], game["name"], game["box_art_url"]) for game in games]

    async def search_channels(
        self, query: str, first: int = 20, live_only: bool = False
    ) -> list[Channel]:
        url = "https://api.twitch.tv/helix/search/channels"
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Client-Id": self._client_id,
        }
        params = {"query": query, "live_only": live_only}

        channels = await http.send_get_with_pagination(url, headers, params, first, 100)

        return [
            Channel(
                User(
                    channel["id"], channel["broadcaster_login"], channel["display_name"]
                ),
                channel["broadcaster_language"],
                Game(channel["game_id"], channel["game_name"]),
                channel["title"],
                channel["tags"],
            )
            for channel in channels
        ]
