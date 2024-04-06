from .._utils import http

DEFAULT_TIMEOUT: int = 10


def get_extension_analytics(
    token: str,
    client_id: str,
    ended_at: str = "",
    extension_id: str = "",
    first: int = 20,
    started_at: str = "",
    report_type: str = "",
) -> list[dict]:
    url = "https://api.twitch.tv/helix/analytics/extensions"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {}

    if ended_at != "":
        params["ended_at"] = ended_at

    if extension_id != "":
        params["extension_id"] = extension_id

    if started_at != "":
        params["started_at"] = started_at

    if report_type != "":
        params["type"] = report_type

    return http.send_get_with_pagination(url, headers, params, first, 100)


def get_game_analytics(
    token: str,
    client_id: str,
    ended_at: str = "",
    first: int = 20,
    game_id: str = "",
    started_at: str = "",
    report_type: str = "",
):
    url = "https://api.twitch.tv/helix/analytics/games"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {}

    if ended_at != "":
        params["ended_at"] = ended_at

    if game_id != "":
        params["game_id"] = game_id

    if started_at != "":
        params["started_at"] = started_at

    if report_type != "":
        params["type"] = report_type

    return http.send_get_with_pagination(url, headers, params, first, 100)
