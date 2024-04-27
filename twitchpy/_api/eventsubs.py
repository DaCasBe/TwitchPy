from datetime import datetime

from .._utils import date, http
from ..dataclasses import Conduit, ConduitShard, EventSubSubscription, Transport

ENDPOINT_CONDUITS = "https://api.twitch.tv/helix/eventsub/conduits"
ENDPOINT_SUBSCRIPTIONS = "https://api.twitch.tv/helix/eventsub/subscriptions"

CONTENT_TYPE_APPLICATION_JSON = "application/json"


def get_conduits(token: str, client_id: str) -> list[Conduit]:
    url = ENDPOINT_CONDUITS
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }

    conduits = http.send_get(url, headers, {})

    return [Conduit(conduit["id"], conduit["shard_count"]) for conduit in conduits]


def create_conduits(token: str, client_id: str, shard_count: int) -> Conduit:
    url = ENDPOINT_CONDUITS
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
        "Content-Type": CONTENT_TYPE_APPLICATION_JSON,
    }
    payload = {"shard_count": shard_count}

    conduit = http.send_post_get_result(url, headers, payload)[0]

    return Conduit(conduit["id"], conduit["shard_count"])


def update_conduits(
    token: str, client_id: str, conduit_id: str, shard_count: int
) -> Conduit:
    url = ENDPOINT_CONDUITS
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
        "Content-Type": CONTENT_TYPE_APPLICATION_JSON,
    }
    data = {"id": conduit_id, "shard_count": shard_count}

    conduit = http.send_patch_get_result(url, headers, data)[0]

    return Conduit(conduit["id"], conduit["shard_count"])


def delete_conduit(token: str, client_id: str, conduit_id: str) -> None:
    url = ENDPOINT_CONDUITS
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    data = {"id": conduit_id}

    http.send_delete(url, headers, data)


def get_conduit_shards(
    token: str, client_id: str, conduit_id: str, status: str | None = None
) -> list[ConduitShard]:
    url = "https://api.twitch.tv/helix/eventsub/conduits/shards"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {"conduit_id": conduit_id}

    if status is not None:
        params["status"] = status

    conduit_shards = http.send_get_with_infinite_pagination(url, headers, params)

    return [
        ConduitShard(
            shard["id"],
            shard["status"],
            Transport(
                shard["transport"]["method"],
                shard["transport"]["callback"],
                shard["transport"]["session_id"],
                datetime.strptime(
                    shard["transport"]["connected_at"], date.RFC3339_FORMAT
                ),
                datetime.strptime(
                    shard["transport"]["disconnected_at"], date.RFC3339_FORMAT
                ),
            ),
        )
        for shard in conduit_shards
    ]


def update_conduit_shards(
    token: str,
    client_id: str,
    conduit_id: str,
    shards: list[ConduitShard],
    session_id: str | None = None,
) -> list[ConduitShard]:
    url = "https://api.twitch.tv/helix/eventsub/conduits/shards"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
        "Content-Type": CONTENT_TYPE_APPLICATION_JSON,
    }
    data = {"conduit_id": conduit_id, "shards": shards}

    if session_id is not None:
        data["session_id"] = session_id

    conduit_shards = http.send_patch_get_result(url, headers, data)

    return [
        ConduitShard(
            shard["id"],
            shard["status"],
            Transport(
                shard["transport"]["method"],
                shard["transport"]["callback"],
                shard["transport"]["session_id"],
                datetime.strptime(
                    shard["transport"]["connected_at"], date.RFC3339_FORMAT
                ),
                datetime.strptime(
                    shard["transport"]["disconnected_at"], date.RFC3339_FORMAT
                ),
            ),
        )
        for shard in conduit_shards
    ]


def create_eventsub_subscription(
    token: str,
    client_id: str,
    subscription_type: str,
    version: str,
    condition: dict,
    transport: Transport,
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
        Transport(
            subscription["transport"]["method"],
            subscription["transport"]["callback"],
            subscription["transport"]["session_id"],
            datetime.strptime(
                subscription["transport"]["connected_at"], date.RFC3339_FORMAT
            ),
            conduit_id=subscription["transport"]["conduit_id"],
        ),
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
    status: str | None = None,
    subscription_type: str | None = None,
    user_id: str | None = None,
) -> list[EventSubSubscription]:
    url = ENDPOINT_SUBSCRIPTIONS
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {}

    if status is not None:
        params["status"] = status

    if subscription_type is not None:
        params["type"] = subscription_type

    if user_id is not None:
        params["user_id"] = user_id

    subscriptions = http.send_get(url, headers, params)

    return [
        EventSubSubscription(
            subscription["id"],
            subscription["status"],
            subscription["type"],
            subscription["version"],
            subscription["condition"],
            datetime.strptime(subscription["created_at"], date.RFC3339_FORMAT),
            Transport(
                subscription["transport"]["method"],
                subscription["transport"]["callback"],
                subscription["transport"]["session_id"],
                datetime.strptime(
                    subscription["transport"]["connected_at"], date.RFC3339_FORMAT
                ),
                datetime.strptime(
                    subscription["transport"]["disconnected_at"], date.RFC3339_FORMAT
                ),
            ),
            subscription["cost"],
        )
        for subscription in subscriptions
    ]
