from .._utils import http
from ..dataclasses import Tag


class TagsAPI:
    def __init__(self, access_token: str, client_id: str):
        self._access_token = access_token
        self._client_id = client_id

    async def get_all_stream_tags(
        self, first: int = 20, tag_id: list[str] | None = None
    ) -> list[Tag]:
        url = "https://api.twitch.tv/helix/tags/streams"
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Client-Id": self._client_id,
        }
        params = {}

        if tag_id is not None and len(tag_id) > 0:
            params["tag_id"] = tag_id

        tags = await http.send_get_with_pagination(url, headers, params, first, 100)

        return [
            Tag(
                tag["tag_id"],
                tag["is_auto"],
                tag["localization_names"],
                tag["localization_descriptions"],
            )
            for tag in tags
        ]

    async def get_stream_tags(self, broadcaster_id: str) -> list[Tag]:
        url = "https://api.twitch.tv/helix/streams/tags"
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Client-Id": self._client_id,
        }
        params = {"broadcaster_id": broadcaster_id}

        tags = await http.send_get(url, headers, params)

        return [
            Tag(
                tag["tag_id"],
                tag["is_auto"],
                tag["localization_names"],
                tag["localization_descriptions"],
            )
            for tag in tags
        ]
