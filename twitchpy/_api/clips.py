from datetime import datetime

from .._utils import http
from ..dataclasses import Channel, Clip, User


def create_clip(
    token: str, client_id: str, broadcaster_id: str, has_delay: bool = False
) -> tuple[str, str]:
    url = "https://api.twitch.tv/helix/clips"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    payload = {"broadcaster_id": broadcaster_id, "has_delay": has_delay}

    clip_creation = http.send_post_get_result(url, headers, payload)[0]

    return (clip_creation["id"], clip_creation["edit_url"])


def get_clips(
    token: str,
    client_id: str,
    broadcaster_id: str | None = None,
    game_id: str | None = None,
    clip_ids: list[str] | None = None,
    started_at: datetime | None = None,
    ended_at: datetime | None = None,
    first: int = 20,
    is_featured: bool | None = None,
) -> list[Clip]:
    url = "https://api.twitch.tv/helix/clips"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {}

    if broadcaster_id is not None:
        params["broadcaster_id"] = broadcaster_id

    if game_id is not None:
        params["game_id"] = game_id

    if clip_ids is not None and len(clip_ids) > 0:
        params["id"] = clip_ids

    if started_at is not None:
        params["started_at"] = started_at

    if ended_at is not None:
        params["ended_at"] = ended_at

    if is_featured is not None:
        params["is_featured"] = is_featured

    clips = http.send_get_with_pagination(url, headers, params, first, 100)

    return [
        Clip(
            clip["id"],
            clip["url"],
            clip["embed_url"],
            Channel(
                User(
                    clip["broadcaster_id"],
                    clip["broadcaster_name"].lower(),
                    clip["broadcaster_name"],
                )
            ),
            User(
                clip["creator_id"], clip["creator_name"].lower(), clip["creator_name"]
            ),
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
