from datetime import datetime

from .._utils import date, http
from ..dataclasses import Conduit, ConduitShard, Transport

ENDPOINT_CONDUITS = "https://api.twitch.tv/helix/eventsub/conduits"

CONTENT_TYPE_APPLICATION_JSON = "application/json"


class ConduitsAPI:
    def __init__(self, access_token: str, client_id: str):
        self._access_token = access_token
        self._client_id = client_id

    async def get_conduits(self) -> list[Conduit]:
        url = ENDPOINT_CONDUITS
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Client-Id": self._client_id,
        }

        conduits = await http.send_get(url, headers, {})

        return [Conduit(conduit["id"], conduit["shard_count"]) for conduit in conduits]

    async def create_conduits(self, shard_count: int) -> Conduit:
        url = ENDPOINT_CONDUITS
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Client-Id": self._client_id,
            "Content-Type": CONTENT_TYPE_APPLICATION_JSON,
        }
        payload = {"shard_count": shard_count}

        conduit = (await http.send_post_get_result(url, headers, payload))[0]

        return Conduit(conduit["id"], conduit["shard_count"])

    async def update_conduits(self, conduit_id: str, shard_count: int) -> Conduit:
        url = ENDPOINT_CONDUITS
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Client-Id": self._client_id,
            "Content-Type": CONTENT_TYPE_APPLICATION_JSON,
        }
        data = {"id": conduit_id, "shard_count": shard_count}

        conduit = (await http.send_patch_get_result(url, headers, data))[0]

        return Conduit(conduit["id"], conduit["shard_count"])

    async def delete_conduit(self, conduit_id: str) -> None:
        url = ENDPOINT_CONDUITS
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Client-Id": self._client_id,
        }
        data = {"id": conduit_id}

        await http.send_delete(url, headers, data)

    async def get_conduit_shards(
        self, conduit_id: str, status: str | None = None
    ) -> list[ConduitShard]:
        url = "https://api.twitch.tv/helix/eventsub/conduits/shards"
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Client-Id": self._client_id,
        }
        params = {"conduit_id": conduit_id}

        if status is not None:
            params["status"] = status

        conduit_shards = await http.send_get_with_infinite_pagination(
            url, headers, params
        )

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

    async def update_conduit_shards(
        self,
        conduit_id: str,
        shards: list[ConduitShard],
        session_id: str | None = None,
    ) -> list[ConduitShard]:
        url = "https://api.twitch.tv/helix/eventsub/conduits/shards"
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Client-Id": self._client_id,
            "Content-Type": CONTENT_TYPE_APPLICATION_JSON,
        }
        data = {"conduit_id": conduit_id, "shards": shards}

        if session_id is not None:
            data["session_id"] = session_id

        conduit_shards = await http.send_patch_get_result(url, headers, data)

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
