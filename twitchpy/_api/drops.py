from datetime import datetime

from .._utils import date, http
from ..dataclasses import DropEntitlement


def get_drops_entitlements(
    token: str,
    client_id: str,
    entitlement_id: list[str] | None = None,
    user_id: str | None = None,
    game_id: str | None = None,
    fulfillment_status: str | None = None,
    first: int = 20,
) -> list[DropEntitlement]:
    url = "https://api.twitch.tv/helix/entitlements/drops"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {}

    if entitlement_id is not None:
        params["id"] = entitlement_id

    if user_id is not None:
        params["user_id"] = user_id

    if game_id is not None:
        params["game_id"] = game_id

    if fulfillment_status is not None:
        params["fulfillment_status"] = fulfillment_status

    drops = http.send_get_with_pagination(url, headers, params, first, 1000)

    return [
        DropEntitlement(
            drop["id"],
            drop["benefit_id"],
            datetime.strptime(drop["timestamp"], date.RFC3339_FORMAT),
            drop["user_id"],
            drop["game_id"],
            drop["fulfillment_status"],
            datetime.strptime(drop["last_updated"], date.RFC3339_FORMAT),
        )
        for drop in drops
    ]


def update_drops_entitlements(
    token: str,
    client_id: str,
    entitlement_ids: list[str] | None = None,
    fulfillment_status: str | None = None,
) -> list[tuple[str, list[str]]]:
    url = "https://api.twitch.tv/helix/entitlements/drops"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
        "Content-Type": "application/json",
    }
    data = {}

    if entitlement_ids is not None and len(entitlement_ids) > 0:
        data["entitlement_ids"] = entitlement_ids

    if fulfillment_status is not None:
        data["fulfillment_status"] = fulfillment_status

    drops_updates = http.send_patch_get_result(url, headers, data)

    return [
        (drop_update["status"], drop_update["ids"]) for drop_update in drops_updates
    ]
