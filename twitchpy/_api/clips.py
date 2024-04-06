from .._utils import http
from ..dataclasses import Clip


def create_clip(
    token: str, client_id: str, broadcaster_id: str, has_delay: bool = False
) -> dict:
    url = "https://api.twitch.tv/helix/clips"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    payload = {}
    payload["broadcaster_id"] = broadcaster_id

    if has_delay is not False:
        payload["has_delay"] = has_delay

    return http.send_post_get_result(url, headers, payload)[0]


def get_clips(
    token: str,
    client_id: str,
    broadcaster_id: str = "",
    game_id: str = "",
    clip_ids: list[str] | None = None,
    started_at: str = "",
    ended_at: str = "",
    first: int = 20,
    is_featured: bool = False,
) -> list[Clip]:
    url = "https://api.twitch.tv/helix/clips"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {}

    if broadcaster_id != "":
        params["broadcaster_id"] = broadcaster_id

    if game_id != "":
        params["game_id"] = game_id

    if clip_ids is not None and len(clip_ids) > 0:
        params["id"] = clip_ids

    if started_at != "":
        params["started_at"] = started_at

    if ended_at != "":
        params["ended_at"] = ended_at

    if is_featured is not False:
        params["is_featured"] = is_featured

    clips = http.send_get_with_pagination(url, headers, params, first, 100)

    return [
        Clip(
            clip["id"],
            clip["url"],
            clip["embed_url"],
            clip["broadcaster_id"],
            clip["broadcaster_name"],
            clip["creator_id"],
            clip["creator_name"],
            clip["video_id"],
            clip["game_id"],
            clip["language"],
            clip["title"],
            clip["view_count"],
            clip["created_at"],
            clip["thumbnail_url"],
            clip["duration"],
            clip["vod_offset"],
            clip["is_featured"],
        )
        for clip in clips
    ]
