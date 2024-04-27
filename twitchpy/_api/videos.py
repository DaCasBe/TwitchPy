from datetime import datetime

from .._utils import date, http
from ..dataclasses import Channel, User, Video


def get_videos(
    token: str,
    client_id: str,
    video_ids: list[str] | None = None,
    user_id: str | None = None,
    game_id: str | None = None,
    first: int = 20,
    language: str | None = None,
    period: str = "all",
    sort: str = "time",
    video_type: str = "all",
) -> list[Video]:
    url = "https://api.twitch.tv/helix/videos"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {}
    params["period"] = period
    params["sort"] = sort
    params["type"] = video_type

    if video_ids is not None and len(video_ids) > 0:
        params["id"] = video_ids

    if user_id is not None:
        params["user_id"] = user_id

    if game_id is not None:
        params["game_id"] = game_id

    if language is not None:
        params["language"] = language

    videos = http.send_get_with_pagination(url, headers, params, first, 100)

    return [
        Video(
            video["id"],
            video["stream_id"],
            Channel(User(video["user_id"], video["user_login"], video["user_name"])),
            video["title"],
            video["description"],
            datetime.strptime(video["created_at"], date.RFC3339_FORMAT),
            datetime.strptime(video["published_at"], date.RFC3339_FORMAT),
            video["url"],
            video["thumbnail_url"],
            video["viewable"],
            video["view_count"],
            video["language"],
            video["type"],
            video["duration"],
            [
                (segment["duration"], segment["offset"])
                for segment in video["muted_segments"]
            ],
        )
        for video in videos
    ]


def delete_video(token: str, client_id: str, video_id: str) -> None:
    url = "https://api.twitch.tv/helix/videos"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    data = {"id": video_id}

    http.send_delete(url, headers, data)
