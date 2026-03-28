from datetime import datetime

from .._utils import date, http
from ..dataclasses import EventSubSubscription, Transport

ENDPOINT_SUBSCRIPTIONS = "https://api.twitch.tv/helix/eventsub/subscriptions"

CONTENT_TYPE_APPLICATION_JSON = "application/json"


class EventSubAPI:
    def __init__(self, access_token: str, client_id: str):
        self._access_token = access_token
        self._client_id = client_id

    async def create_eventsub_subscription(
        self,
        subscription_type: str,
        version: str,
        condition: dict,
        transport: Transport,
    ) -> EventSubSubscription:
        url = ENDPOINT_SUBSCRIPTIONS
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Client-Id": self._client_id,
            "Content-Type": CONTENT_TYPE_APPLICATION_JSON,
        }
        payload = {
            "type": subscription_type,
            "version": version,
            "condition": condition,
            "transport": transport,
        }

        subscription = (await http.send_post_get_result(url, headers, payload))[0]

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

    async def delete_eventsub_subscription(self, subscription_id: str) -> None:
        url = ENDPOINT_SUBSCRIPTIONS
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Client-Id": self._client_id,
        }
        data = {"id": subscription_id}

        await http.send_delete(url, headers, data)

    async def get_eventsub_subscriptions(
        self,
        status: str | None = None,
        subscription_type: str | None = None,
        user_id: str | None = None,
    ) -> list[EventSubSubscription]:
        url = ENDPOINT_SUBSCRIPTIONS
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Client-Id": self._client_id,
        }
        params = {}

        if status is not None:
            params["status"] = status

        if subscription_type is not None:
            params["type"] = subscription_type

        if user_id is not None:
            params["user_id"] = user_id

        subscriptions = await http.send_get(url, headers, params)

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
                        subscription["transport"]["disconnected_at"],
                        date.RFC3339_FORMAT,
                    ),
                ),
                subscription["cost"],
            )
            for subscription in subscriptions
        ]
