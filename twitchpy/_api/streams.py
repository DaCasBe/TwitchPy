import re
from datetime import datetime

from .._utils import date, http
from ..dataclasses import Channel, Game, Stream, StreamMarker, User


class StreamsAPI:
    def __init__(self, access_token: str, client_id: str):
        self._access_token = access_token
        self._client_id = client_id

    async def get_stream_key(self, broadcaster_id: str) -> str:
        url = "https://api.twitch.tv/helix/streams/key"
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Client-Id": self._client_id,
        }
        params = {"broadcaster_id": broadcaster_id}

        return (await http.send_get(url, headers, params))[0]["stream_key"]

    async def get_streams(
        self,
        user_id: list[str] | None = None,
        user_login: list[str] | None = None,
        game_id: list[str] | None = None,
        stream_type: str = "all",
        language: list[str] | None = None,
        first: int = 20,
    ) -> list[Stream]:
        url = "https://api.twitch.tv/helix/streams"
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Client-Id": self._client_id,
        }
        params = {}
        params["stream_type"] = stream_type

        if user_id is not None:
            params["user_id"] = user_id

        if user_login is not None:
            params["user_login"] = user_login

        if game_id is not None:
            params["game_id"] = game_id

        if language is not None:
            params["language"] = language

        streams = await http.send_get_with_pagination(url, headers, params, first, 100)

        return [
            Stream(
                stream["id"],
                Channel(
                    User(stream["user_id"], stream["user_login"], stream["user_name"])
                ),
                Game(stream["game_id"], stream["game_name"]),
                stream["type"],
                stream["title"],
                stream["tags"],
                stream["viewer_count"],
                datetime.strptime(stream["started_at"], date.RFC3339_FORMAT),
                stream["language"],
                stream["thumbnail_url"],
                stream["is_mature"],
            )
            for stream in streams
        ]

    async def get_followed_streams(
        self, user_id: str, first: int = 100
    ) -> list[Stream]:
        url = "https://api.twitch.tv/helix/streams/followed"
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Client-Id": self._client_id,
        }
        params = {"user_id": user_id}

        streams = await http.send_get_with_pagination(url, headers, params, first, 100)

        return [
            Stream(
                stream["id"],
                Channel(
                    User(stream["user_id"], stream["user_login"], stream["user_name"])
                ),
                Game(stream["game_id"], stream["game_name"]),
                stream["type"],
                stream["title"],
                stream["tags"],
                stream["viewer_count"],
                datetime.strptime(stream["started_at"], date.RFC3339_FORMAT),
                stream["language"],
                stream["thumbnail_url"],
                stream["is_mature"],
            )
            for stream in streams
        ]

    async def create_stream_marker(
        self, user_id: str, description: str | None = None
    ) -> StreamMarker:
        url = "https://api.twitch.tv/helix/streams/markers"
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Client-Id": self._client_id,
            "Content-Type": "application/json",
        }
        payload = {"user_id": user_id}

        if description is not None:
            payload["description"] = description

        marker = (await http.send_post_get_result(url, headers, payload))[0]

        # Twitch documentation says that the created_at time is
        # RFC3339 but it also includes nanoseconds. This removes
        # the nanoseconds from the end
        # https://discuss.dev.twitch.com/t/create-stream-marker-api-response-incorrect-format/62671

        new_time = re.sub(r"\.\d+Z$", "Z", marker["created_at"])

        return StreamMarker(
            marker["id"],
            datetime.strptime(new_time, date.RFC3339_FORMAT),
            marker["position_seconds"],
            marker["description"],
        )

    async def get_stream_markers(
        self,
        user_id: str | None = None,
        video_id: str | None = None,
        first: int = 20,
    ) -> list[dict]:
        url = "https://api.twitch.tv/helix/streams/markers"
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Client-Id": self._client_id,
        }
        params = {}

        if user_id is not None:
            params["user_id"] = user_id

        if video_id is not None:
            params["video_id"] = video_id

        return await http.send_get_with_pagination(url, headers, params, first, 100)
