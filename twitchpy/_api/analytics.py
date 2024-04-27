from datetime import datetime

from .._utils import date, http
from ..dataclasses import ExtensionAnalyticsReport, GameAnalyticsReport


def get_extension_analytics(
    token: str,
    client_id: str,
    extension_id: str | None = None,
    report_type: str | None = None,
    started_at: datetime | None = None,
    ended_at: datetime | None = None,
    first: int = 20,
) -> list[ExtensionAnalyticsReport]:
    url = "https://api.twitch.tv/helix/analytics/extensions"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {}

    if extension_id is not None:
        params["extension_id"] = extension_id

    if report_type is not None:
        params["type"] = report_type

    if started_at is not None:
        params["started_at"] = started_at

    if ended_at is not None:
        params["ended_at"] = ended_at

    reports = http.send_get_with_pagination(url, headers, params, first, 100)

    return [
        ExtensionAnalyticsReport(
            report["extension_id"],
            report["URL"],
            report["type"],
            datetime.strptime(report["date_range"]["started_at"], date.RFC3339_FORMAT),
            datetime.strptime(report["date_range"]["ended_at"], date.RFC3339_FORMAT),
        )
        for report in reports
    ]


def get_game_analytics(
    token: str,
    client_id: str,
    game_id: str | None = None,
    report_type: str | None = None,
    started_at: datetime | None = None,
    ended_at: datetime | None = None,
    first: int = 20,
) -> list[GameAnalyticsReport]:
    url = "https://api.twitch.tv/helix/analytics/games"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {}

    if game_id is not None:
        params["game_id"] = game_id

    if report_type is not None:
        params["type"] = report_type

    if started_at is not None:
        params["started_at"] = started_at

    if ended_at is not None:
        params["ended_at"] = ended_at

    reports = http.send_get_with_pagination(url, headers, params, first, 100)

    return [
        GameAnalyticsReport(
            report["game_id"],
            report["URL"],
            report["type"],
            datetime.strptime(report["date_range"]["started_at"], date.RFC3339_FORMAT),
            datetime.strptime(report["date_range"]["ended_at"], date.RFC3339_FORMAT),
        )
        for report in reports
    ]
