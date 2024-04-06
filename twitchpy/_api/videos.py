from .._utils import http
from ..dataclasses import Video


def get_videos(
    token: str,
    client_id: str,
    video_ids: list[str] | None = None,
    user_id: str = "",
    game_id: str = "",
    first: int = 20,
    language: str = "",
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

    if video_ids is not None and len(video_ids) > 0:
        params["id"] = video_ids

    if user_id != "":
        params["user_id"] = user_id

    if game_id != "":
        params["game_id"] = game_id

    if language != "":
        params["language"] = language

    if period != "all":
        params["period"] = period

    if sort != "time":
        params["sort"] = sort

    if video_type != "all":
        params["type"] = video_type

    videos = http.send_get_with_pagination(url, headers, params, first, 100)

    return [
        Video(
            video["id"],
            video["user_id"],
            video["user_name"],
            video["title"],
            video["description"],
            video["created_at"],
            video["published_at"],
            video["url"],
            video["thumbnail_url"],
            video["viewable"],
            video["view_count"],
            video["language"],
            video["type"],
            video["duration"],
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
