from datetime import datetime

from .._utils import http
from ..dataclasses import BitsLeaderboardLeader, Cheermote, CheermoteTier, User


def get_bits_leaderboard(
    token: str,
    client_id: str,
    count: int = 10,
    period: str = "all",
    started_at: datetime | None = None,
    user_id: str | None = None,
) -> list[BitsLeaderboardLeader]:
    url = "https://api.twitch.tv/helix/bits/leaderboard"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {"count": count, "period": period}

    if started_at is not None:
        params["started_at"] = started_at

    if user_id is not None:
        params["user_id"] = user_id

    leaderboard = http.send_get(url, headers, params)

    return [
        BitsLeaderboardLeader(
            User(leader["user_id"], leader["user_login"], leader["user_name"]),
            leader["rank"],
            leader["score"],
        )
        for leader in leaderboard
    ]


def get_cheermotes(
    token: str, client_id: str, broadcaster_id: str | None = None
) -> list[Cheermote]:
    url = "https://api.twitch.tv/helix/bits/cheermotes"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {}

    if broadcaster_id is not None:
        params = {"broadcaster_id": broadcaster_id}

    cheermotes = http.send_get(url, headers, params)

    return [
        Cheermote(
            cheermote["prefix"],
            [
                CheermoteTier(
                    tier["min_bits"],
                    tier["tier_id"],
                    tier["color"],
                    tier["images"],
                    tier["can_cheer"],
                    tier["show_in_bits_card"],
                )
                for tier in cheermote["tier"]
            ],
            cheermote["type"],
            cheermote["order"],
            cheermote["last_updated"],
            cheermote["is_charitable"],
        )
        for cheermote in cheermotes
    ]
