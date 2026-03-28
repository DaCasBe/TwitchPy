from datetime import datetime

from .._utils import date, http
from ..dataclasses import (Guest, GuestStarInvite, GuestStarSession,
                           GuestStarSettings, User)

ENDPOINT_SESSIONS = "https://api.twitch.tv/helix/guest_star/session"
ENDPOINT_INVITES = "https://api.twitch.tv/helix/guest_star/invites"
ENDPOINT_SLOTS = "https://api.twitch.tv/helix/guest_star/slot"


class GuestStarAPI:
    def __init__(self, access_token: str, client_id: str):
        self._access_token = access_token
        self._client_id = client_id

    async def get_channel_guest_star_settings(
        self, broadcaster_id: str, moderator_id: str
    ) -> GuestStarSettings:
        url = "https://api.twitch.tv/helix/guest_star/channel_settings"
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Client-Id": self._client_id,
        }
        params = {"broadcaster_id": broadcaster_id, "moderator_id": moderator_id}

        settings = (await http.send_get(url, headers, params))[0]

        return GuestStarSettings(
            settings["is_moderator_send_live_enabled"],
            settings["slot_count"],
            settings["is_browser_source_audio_enabled"],
            settings["group_layout"],
            settings["browser_source_token"],
        )

    async def update_channel_guest_star_settings(
        self,
        broadcaster_id: str,
        is_moderator_send_live_enabled: bool | None = None,
        slot_count: int | None = None,
        is_browser_source_audio_enabled: bool | None = None,
        group_layout: str | None = None,
        regenerate_browser_sources: bool | None = None,
    ) -> None:
        url = "https://api.twitch.tv/helix/guest_star/channel_settings"
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Client-Id": self._client_id,
        }
        data = {}
        data["broadcaster_id"] = broadcaster_id

        if is_moderator_send_live_enabled is not None:
            data["is_moderator_send_live_enabled"] = is_moderator_send_live_enabled

        if slot_count is not None:
            data["slot_count"] = slot_count

        if is_browser_source_audio_enabled is not None:
            data["is_browser_source_audio_enabled"] = is_browser_source_audio_enabled

        if group_layout is not None:
            data["group_layout"] = group_layout

        if regenerate_browser_sources is not None:
            data["regenerate_browser_sources"] = regenerate_browser_sources

        await http.send_put(url, headers, data)

    async def get_guest_star_session(
        self, broadcaster_id: str, moderator_id: str
    ) -> GuestStarSession:
        url = ENDPOINT_SESSIONS
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Client-Id": self._client_id,
        }
        params = {"broadcaster_id": broadcaster_id, "moderator_id": moderator_id}

        session = (await http.send_get(url, headers, params))[0]

        return GuestStarSession(
            session["id"],
            [
                Guest(
                    guest["slot_id"],
                    guest["is_live"],
                    User(
                        guest["user_id"],
                        guest["user_login"],
                        guest["user_display_name"],
                    ),
                    guest["volume"],
                    datetime.strptime(guest["assigned_at"], date.RFC3339_FORMAT),
                    guest["audio_settings"],
                    guest["video_settings"],
                )
                for guest in session["guests"]
            ],
        )

    async def create_guest_star_session(self, broadcaster_id: str) -> GuestStarSession:
        url = ENDPOINT_SESSIONS
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Client-Id": self._client_id,
        }
        payload = {"broadcaster_id": broadcaster_id}

        session = (await http.send_post_get_result(url, headers, payload))[0]

        return GuestStarSession(
            session["id"],
            [
                Guest(
                    guest["slot_id"],
                    guest["is_live"],
                    User(
                        guest["user_id"],
                        guest["user_login"],
                        guest["user_display_name"],
                    ),
                    guest["volume"],
                    datetime.strptime(guest["assigned_at"], date.RFC3339_FORMAT),
                    guest["audio_settings"],
                    guest["video_settings"],
                )
                for guest in session["guests"]
            ],
        )

    async def end_guest_star_session(
        self, broadcaster_id: str, session_id: str
    ) -> GuestStarSession:
        url = ENDPOINT_SESSIONS
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Client-Id": self._client_id,
        }
        data = {"broadcaster_id": broadcaster_id, "session_id": session_id}

        session = (await http.send_delete_get_result(url, headers, data))[0]

        return GuestStarSession(
            session["id"],
            [
                Guest(
                    guest["slot_id"],
                    guest["is_live"],
                    User(
                        guest["user_id"],
                        guest["user_login"],
                        guest["user_display_name"],
                    ),
                    guest["volume"],
                    datetime.strptime(guest["assigned_at"], date.RFC3339_FORMAT),
                    guest["audio_settings"],
                    guest["video_settings"],
                )
                for guest in session["guests"]
            ],
        )

    async def get_guest_star_invites(
        self,
        broadcaster_id: str,
        moderator_id: str,
        session_id: str,
    ) -> list[GuestStarInvite]:
        url = ENDPOINT_INVITES
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Client-Id": self._client_id,
        }
        params = {
            "broadcaster_id": broadcaster_id,
            "moderator_id": moderator_id,
            "session_id": session_id,
        }

        invites = await http.send_get(url, headers, params)

        return [
            GuestStarInvite(
                invite["user_id"],
                datetime.strptime(invite["invited_at"], date.RFC3339_FORMAT),
                invite["status"],
                invite["is_video_enabled"],
                invite["is_audio_enabled"],
                invite["is_video_available"],
                invite["is_audio_available"],
            )
            for invite in invites
        ]

    async def send_guest_star_invite(
        self,
        broadcaster_id: str,
        moderator_id: str,
        session_id: str,
        guest_id: str,
    ) -> None:
        url = ENDPOINT_INVITES
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Client-Id": self._client_id,
        }
        payload = {
            "broadcaster_id": broadcaster_id,
            "moderator_id": moderator_id,
            "session_id": session_id,
            "guest_id": guest_id,
        }

        await http.send_post(url, headers, payload)

    async def delete_guest_star_invite(
        self,
        broadcaster_id: str,
        moderator_id: str,
        session_id: str,
        guest_id: str,
    ) -> None:
        url = ENDPOINT_INVITES
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Client-Id": self._client_id,
        }
        data = {
            "broadcaster_id": broadcaster_id,
            "moderator_id": moderator_id,
            "session_id": session_id,
            "guest_id": guest_id,
        }

        await http.send_delete(url, headers, data)

    async def assign_guest_star_slot(
        self,
        broadcaster_id: str,
        moderator_id: str,
        session_id: str,
        guest_id: str,
        slot_id: str,
    ) -> None:
        url = ENDPOINT_SLOTS
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Client-Id": self._client_id,
        }
        payload = {
            "broadcaster_id": broadcaster_id,
            "moderator_id": moderator_id,
            "session_id": session_id,
            "guest_id": guest_id,
            "slot_id": slot_id,
        }

        await http.send_post(url, headers, payload)

    async def update_guest_star_slot(
        self,
        broadcaster_id: str,
        moderator_id: str,
        session_id: str,
        source_slot_id: str,
        destination_slot_id: str | None = None,
    ) -> None:
        url = ENDPOINT_SLOTS
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Client-Id": self._client_id,
        }
        data = {
            "broadcaster_id": broadcaster_id,
            "moderator_id": moderator_id,
            "session_id": session_id,
            "source_slot_id": source_slot_id,
        }

        if destination_slot_id is not None:
            data["destination_slot_id"] = destination_slot_id

        await http.send_patch(url, headers, data)

    async def delete_guest_star_slot(
        self,
        broadcaster_id: str,
        moderator_id: str,
        session_id: str,
        guest_id: str,
        slot_id: str,
        should_reinvite_guest: str | None = None,
    ) -> None:
        url = ENDPOINT_SLOTS
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Client-Id": self._client_id,
        }
        data = {
            "broadcaster_id": broadcaster_id,
            "moderator_id": moderator_id,
            "session_id": session_id,
            "guest_id": guest_id,
            "slot_id": slot_id,
        }

        if should_reinvite_guest is not None:
            data["should_reinvite_guest"] = should_reinvite_guest

        await http.send_delete(url, headers, data)

    async def update_guest_star_slot_settings(
        self,
        broadcaster_id: str,
        moderator_id: str,
        session_id: str,
        slot_id: str,
        is_audio_enabled: bool | None = None,
        is_video_enabled: bool | None = None,
        is_live: bool | None = None,
        volume: int | None = None,
    ) -> None:
        url = "https://api.twitch.tv/helix/guest_star/slot_settings"
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Client-Id": self._client_id,
        }
        data = {}
        data["broadcaster_id"] = broadcaster_id
        data["moderator_id"] = moderator_id
        data["session_id"] = session_id
        data["slot_id"] = slot_id

        if is_audio_enabled is not None:
            data["is_audio_enabled"] = is_audio_enabled

        if is_video_enabled is not None:
            data["is_video_enabled"] = is_video_enabled

        if is_live is not None:
            data["is_live"] = is_live

        if volume is not None:
            data["volume"] = volume

        await http.send_patch(url, headers, data)
