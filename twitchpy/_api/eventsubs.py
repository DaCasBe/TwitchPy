from .._utils import http
from ..dataclasses import EventSubSubscription

ENDPOINT_CONDUITS = "https://api.twitch.tv/helix/eventsub/conduits"
ENDPOINT_SUBSCRIPTIONS = "https://api.twitch.tv/helix/eventsub/subscriptions"

CONTENT_TYPE_APPLICATION_JSON = "application/json"


def get_conduits(token: str, client_id: str) -> list[dict]:
    url = ENDPOINT_CONDUITS
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }

    return http.send_get(url, headers, {})


def create_conduits(token: str, client_id: str, shard_count: int) -> dict:
    url = ENDPOINT_CONDUITS
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
        "Content-Type": CONTENT_TYPE_APPLICATION_JSON,
    }
    payload = {"shard_count": shard_count}

    return http.send_post_get_result(url, headers, payload)[0]


def update_conduits(
    token: str, client_id: str, conduit_id: str, shard_count: int
) -> dict:
    url = ENDPOINT_CONDUITS
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
        "Content-Type": CONTENT_TYPE_APPLICATION_JSON,
    }
    data = {"id": conduit_id, "shard_count": shard_count}

    return http.send_patch_get_result(url, headers, data)[0]


def delete_conduit(token: str, client_id: str, conduit_id: str) -> None:
    url = ENDPOINT_CONDUITS
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    data = {"id": conduit_id}

    http.send_delete(url, headers, data)


def get_conduit_shards(
    token: str, client_id: str, conduit_id: str, status: str = ""
) -> list[dict]:
    url = "https://api.twitch.tv/helix/eventsub/conduits/shards"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {"conduit_id": conduit_id}

    if status != "":
        params["status"] = status

    return http.send_get_with_infinite_pagination(url, headers, params)


def update_conduit_shards(
    token: str,
    client_id: str,
    conduit_id: str,
    shards: list[dict],
    session_id: str = "",
) -> list[dict]:
    url = "https://api.twitch.tv/helix/eventsub/conduits/shards"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
        "Content-Type": CONTENT_TYPE_APPLICATION_JSON,
    }
    data = {"conduit_id": conduit_id, "shards": shards}

    if session_id != "":
        data["session_id"] = session_id

    return http.send_patch_get_result(url, headers, data)


def create_eventsub_subscription(
    token: str,
    client_id: str,
    subscription_type: str,
    version: str,
    condition: dict,
    transport: dict,
) -> EventSubSubscription:
    url = ENDPOINT_SUBSCRIPTIONS
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
        "Content-Type": CONTENT_TYPE_APPLICATION_JSON,
    }
    payload = {
        "type": subscription_type,
        "version": version,
        "condition": condition,
        "transport": transport,
    }

    subscription = http.send_post_get_result(url, headers, payload)[0]

    return EventSubSubscription(
        subscription["id"],
        subscription["status"],
        subscription["type"],
        subscription["version"],
        subscription["condition"],
        subscription["created_at"],
        subscription["transport"],
        subscription["cost"],
    )


def delete_eventsub_subscription(
    token: str, client_id: str, subscription_id: str
) -> None:
    url = ENDPOINT_SUBSCRIPTIONS
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    data = {"id": subscription_id}

    http.send_delete(url, headers, data)


def get_eventsub_subscriptions(
    token: str,
    client_id: str,
    status: str = "",
    subscription_type: str = "",
    user_id: str = "",
) -> list[EventSubSubscription]:
    url = ENDPOINT_SUBSCRIPTIONS
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {}

    if status != "":
        params["status"] = status

    if subscription_type != "":
        params["type"] = subscription_type

    if user_id != "":
        params["user_id"] = user_id

    subscriptions = http.send_get(url, headers, params)

    return [
        EventSubSubscription(
            subscription["id"],
            subscription["status"],
            subscription["type"],
            subscription["version"],
            subscription["condition"],
            subscription["created_at"],
            subscription["transport"],
            subscription["cost"],
        )
        for subscription in subscriptions
    ]
