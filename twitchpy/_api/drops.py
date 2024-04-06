from .._utils import http


def get_drops_entitlements(
    token: str,
    client_id: str,
    entitlement_id: str = "",
    user_id: str = "",
    game_id: str = "",
    fulfillment_status: str = "",
    first: int = 20,
) -> list[dict]:
    url = "https://api.twitch.tv/helix/entitlements/drops"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {}

    if entitlement_id != "":
        params["id"] = entitlement_id

    if user_id != "":
        params["user_id"] = user_id

    if game_id != "":
        params["game_id"] = game_id

    if fulfillment_status != "":
        params["fulfillment_status"] = fulfillment_status

    return http.send_get_with_pagination(url, headers, params, first, 1000)


def update_drops_entitlements(
    token: str,
    client_id: str,
    entitlement_ids: list[str] | None = None,
    fulfillment_status: str = "",
) -> list[dict]:
    url = "https://api.twitch.tv/helix/entitlements/drops"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
        "Content-Type": "application/json",
    }
    data = {}

    if entitlement_ids is not None and len(entitlement_ids) > 0:
        data["entitlement_ids"] = entitlement_ids

    if fulfillment_status != "":
        data["fulfillment_status"] = fulfillment_status

    return http.send_patch_get_result(url, headers, data)
