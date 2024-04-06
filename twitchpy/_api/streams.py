from .._utils import http
from ..dataclasses import Stream


def get_stream_key(token: str, client_id: str, broadcaster_id: str) -> str:
    url = "https://api.twitch.tv/helix/streams/key"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {"broadcaster_id": broadcaster_id}

    return http.send_get(url, headers, params)[0]["stream_key"]


def get_streams(
    token: str,
    client_id: str,
    user_id: str | list[str] = "",
    user_login: str | list[str] = "",
    game_id: str | list[str] = "",
    stream_type: str = "all",
    language: str | list[str] = "",
    first: int = 20,
) -> list[Stream]:
    url = "https://api.twitch.tv/helix/streams"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {}

    if user_id != "":
        params["user_id"] = user_id

    if user_login != "":
        params["user_login"] = user_login

    if game_id != "":
        params["game_id"] = game_id

    if stream_type != "all":
        params["type"] = stream_type

    if language != "":
        params["language"] = language

    streams = http.send_get_with_pagination(url, headers, params, first, 100)

    return [
        Stream(
            stream["id"],
            stream["user_id"],
            stream["user_login"],
            stream["user_name"],
            stream["game_id"],
            stream["game_name"],
            stream["type"],
            stream["title"],
            stream["tags"],
            stream["viewer_count"],
            stream["started_at"],
            stream["language"],
            stream["thumbnail_url"],
            stream["is_mature"],
        )
        for stream in streams
    ]


def get_followed_streams(
    token: str, client_id: str, user_id: str, first: int = 100
) -> list[Stream]:
    url = "https://api.twitch.tv/helix/streams/followed"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {"user_id": user_id}

    streams = http.send_get_with_pagination(url, headers, params, first, 100)

    return [
        Stream(
            stream["id"],
            stream["user_id"],
            stream["user_login"],
            stream["user_name"],
            stream["game_id"],
            stream["game_name"],
            stream["type"],
            stream["title"],
            stream["tags"],
            stream["viewer_count"],
            stream["started_at"],
            stream["language"],
            stream["thumbnail_url"],
            stream["is_mature"],
        )
        for stream in streams
    ]


def create_stream_marker(
    token: str, client_id: str, user_id: str, description: str = ""
) -> dict:
    url = "https://api.twitch.tv/helix/streams/markers"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
        "Content-Type": "application/json",
    }
    payload = {"user_id": user_id}

    if description != "":
        payload["description"] = description

    return http.send_post_get_result(url, headers, payload)[0]


def get_stream_markers(
    token: str, client_id: str, user_id: str = "", video_id: str = "", first: int = 20
) -> list[dict]:
    url = "https://api.twitch.tv/helix/streams/markers"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {}

    if user_id != "":
        params["user_id"] = user_id

    if video_id != "":
        params["video_id"] = video_id

    return http.send_get_with_pagination(url, headers, params, first, 100)
