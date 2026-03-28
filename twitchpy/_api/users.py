from datetime import datetime

from .._utils import date, http
from ..dataclasses import User

ENDPOINT_BLOCKS = "https://api.twitch.tv/helix/users/blocks"


class UsersAPI:
    def __init__(self, access_token: str, client_id: str):
        self._access_token = access_token
        self._client_id = client_id

    async def get_users(
        self,
        user_ids: list[str] | None = None,
        login: list[str] | None = None,
    ) -> list[User]:
        url = "https://api.twitch.tv/helix/users"
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Client-Id": self._client_id,
        }
        params = {}

        if user_ids is not None and len(user_ids) > 0:
            params["id"] = user_ids

        if login is not None and len(login) > 0:
            params["login"] = [
                user_login.replace("@", "").lower() for user_login in login
            ]

        users = await http.send_get(url, headers, params)

        return [
            User(
                user["id"],
                user["login"],
                user["display_name"],
                user["type"],
                user["broadcaster_type"],
                user["description"],
                user["profile_image_url"],
                user["offline_image_url"],
                user["view_count"],
                user["email"] if "email" in user else None,
                datetime.strptime(user["created_at"], date.RFC3339_FORMAT),
            )
            for user in users
        ]

    async def update_user(self, description: str | None = None) -> User:
        url = "https://api.twitch.tv/helix/users"
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Client-Id": self._client_id,
        }
        data = {}

        if description != "":
            data = {"description": description}

        user = (await http.send_put_get_result(url, headers, data))[0]

        return User(
            user["id"],
            user["login"],
            user["display_name"],
            user["type"],
            user["broadcaster_type"],
            user["description"],
            user["profile_image_url"],
            user["offline_image_url"],
            user["view_count"],
            user["email"],
            datetime.strptime(user["created_at"], date.RFC3339_FORMAT),
        )

    async def get_user_block_list(
        self, broadcaster_id: str, first: int = 20
    ) -> list[User]:
        url = ENDPOINT_BLOCKS
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Client-Id": self._client_id,
        }
        params = {}
        params["broadcaster_id"] = broadcaster_id

        if first != 20:
            params["first"] = first

        users = await http.send_get_with_pagination(url, headers, params, first, 100)

        return [
            User(user["user_id"], user["user_login"], user["display_name"])
            for user in users
        ]

    async def block_user(
        self,
        target_user_id: str,
        source_context: str | None = None,
        reason: str | None = None,
    ) -> None:
        url = ENDPOINT_BLOCKS
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Client-Id": self._client_id,
        }
        data = {"target_user_id": target_user_id}

        if source_context is not None:
            data["source_context"] = source_context

        if reason is not None:
            data["reason"] = reason

        await http.send_put(url, headers, data)

    async def unblock_user(self, target_user_id: str) -> None:
        url = ENDPOINT_BLOCKS
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Client-Id": self._client_id,
        }
        data = {"target_user_id": target_user_id}

        await http.send_delete(url, headers, data)

    async def get_user_extensions(self) -> list[dict]:
        url = "https://api.twitch.tv/helix/users/extensions/list"
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Client-Id": self._client_id,
        }

        return await http.send_get(url, headers, {})

    async def get_user_active_extensions(
        self, user_id: str | None = None
    ) -> list[dict]:
        url = "https://api.twitch.tv/helix/users/extensions"
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Client-Id": self._client_id,
        }
        params = {}

        if user_id != "":
            params = {"user_id": user_id}

        return await http.send_get(url, headers, params)

    async def update_user_extensions(self, data: dict) -> list[dict]:
        url = "https://api.twitch.tv/helix/users/extensions"
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Client-Id": self._client_id,
            "Content-Type": "application/json",
        }
        data = {"data": data}

        return await http.send_put_get_result(url, headers, {})
