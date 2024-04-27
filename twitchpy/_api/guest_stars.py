from datetime import datetime

from .._utils import date, http
from ..dataclasses import (
    Guest,
    GuestStarInvite,
    GuestStarSession,
    GuestStarSettings,
    User,
)

ENDPOINT_SESSIONS = "https://api.twitch.tv/helix/guest_star/session"
ENDPOINT_INVITES = "https://api.twitch.tv/helix/guest_star/invites"
ENDPOINT_SLOTS = "https://api.twitch.tv/helix/guest_star/slot"


def get_channel_guest_star_settings(
    token: str, client_id: str, broadcaster_id: str, moderator_id: str
) -> GuestStarSettings:
    url = "https://api.twitch.tv/helix/guest_star/channel_settings"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {"broadcaster_id": broadcaster_id, "moderator_id": moderator_id}

    settings = http.send_get(url, headers, params)[0]

    return GuestStarSettings(
        settings["is_moderator_send_live_enabled"],
        settings["slot_count"],
        settings["is_browser_source_audio_enabled"],
        settings["group_layout"],
        settings["browser_source_token"],
    )


def update_channel_guest_star_settings(
    token: str,
    client_id: str,
    broadcaster_id: str,
    is_moderator_send_live_enabled: bool | None = None,
    slot_count: int | None = None,
    is_browser_source_audio_enabled: bool | None = None,
    group_layout: str | None = None,
    regenerate_browser_sources: bool | None = None,
) -> None:
    url = "https://api.twitch.tv/helix/guest_star/channel_settings"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
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

    http.send_put(url, headers, data)


def get_guest_star_session(
    token: str, client_id: str, broadcaster_id: str, moderator_id: str
) -> GuestStarSession:
    url = ENDPOINT_SESSIONS
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {"broadcaster_id": broadcaster_id, "moderator_id": moderator_id}

    session = http.send_get(url, headers, params)[0]

    return GuestStarSession(
        session["id"],
        [
            Guest(
                guest["slot_id"],
                guest["is_live"],
                User(guest["user_id"], guest["user_login"], guest["user_display_name"]),
                guest["volume"],
                datetime.strptime(guest["assigned_at"], date.RFC3339_FORMAT),
                guest["audio_settings"],
                guest["video_settings"],
            )
            for guest in session["guests"]
        ],
    )


def create_guest_star_session(
    token: str, client_id: str, broadcaster_id: str
) -> GuestStarSession:
    url = ENDPOINT_SESSIONS
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    payload = {"broadcaster_id": broadcaster_id}

    session = http.send_post_get_result(url, headers, payload)[0]

    return GuestStarSession(
        session["id"],
        [
            Guest(
                guest["slot_id"],
                guest["is_live"],
                User(guest["user_id"], guest["user_login"], guest["user_display_name"]),
                guest["volume"],
                datetime.strptime(guest["assigned_at"], date.RFC3339_FORMAT),
                guest["audio_settings"],
                guest["video_settings"],
            )
            for guest in session["guests"]
        ],
    )


def end_guest_star_session(
    token: str, client_id: str, broadcaster_id: str, session_id: str
) -> GuestStarSession:
    url = ENDPOINT_SESSIONS
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    data = {"broadcaster_id": broadcaster_id, "session_id": session_id}

    session = http.send_delete_get_result(url, headers, data)[0]

    return GuestStarSession(
        session["id"],
        [
            Guest(
                guest["slot_id"],
                guest["is_live"],
                User(guest["user_id"], guest["user_login"], guest["user_display_name"]),
                guest["volume"],
                datetime.strptime(guest["assigned_at"], date.RFC3339_FORMAT),
                guest["audio_settings"],
                guest["video_settings"],
            )
            for guest in session["guests"]
        ],
    )


def get_guest_star_invites(
    token: str, client_id: str, broadcaster_id: str, moderator_id: str, session_id: str
) -> list[GuestStarInvite]:
    url = ENDPOINT_INVITES
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {
        "broadcaster_id": broadcaster_id,
        "moderator_id": moderator_id,
        "session_id": session_id,
    }

    invites = http.send_get(url, headers, params)

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


def send_guest_star_invite(
    token: str,
    client_id: str,
    broadcaster_id: str,
    moderator_id: str,
    session_id: str,
    guest_id: str,
) -> None:
    url = ENDPOINT_INVITES
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    payload = {
        "broadcaster_id": broadcaster_id,
        "moderator_id": moderator_id,
        "session_id": session_id,
        "guest_id": guest_id,
    }

    http.send_post(url, headers, payload)


def delete_guest_star_invite(
    token: str,
    client_id: str,
    broadcaster_id: str,
    moderator_id: str,
    session_id: str,
    guest_id: str,
) -> None:
    url = ENDPOINT_INVITES
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    data = {
        "broadcaster_id": broadcaster_id,
        "moderator_id": moderator_id,
        "session_id": session_id,
        "guest_id": guest_id,
    }

    http.send_delete(url, headers, data)


def assign_guest_star_slot(
    token: str,
    client_id: str,
    broadcaster_id: str,
    moderator_id: str,
    session_id: str,
    guest_id: str,
    slot_id: str,
) -> None:
    url = ENDPOINT_SLOTS
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    payload = {
        "broadcaster_id": broadcaster_id,
        "moderator_id": moderator_id,
        "session_id": session_id,
        "guest_id": guest_id,
        "slot_id": slot_id,
    }

    http.send_post(url, headers, payload)


def update_guest_star_slot(
    token: str,
    client_id: str,
    broadcaster_id: str,
    moderator_id: str,
    session_id: str,
    source_slot_id: str,
    destination_slot_id: str | None = None,
) -> None:
    url = ENDPOINT_SLOTS
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    data = {
        "broadcaster_id": broadcaster_id,
        "moderator_id": moderator_id,
        "session_id": session_id,
        "source_slot_id": source_slot_id,
    }

    if destination_slot_id is not None:
        data["destination_slot_id"] = destination_slot_id

    http.send_patch(url, headers, data)


def delete_guest_star_slot(
    token: str,
    client_id: str,
    broadcaster_id: str,
    moderator_id: str,
    session_id: str,
    guest_id: str,
    slot_id: str,
    should_reinvite_guest: str | None = None,
) -> None:
    url = ENDPOINT_SLOTS
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
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

    http.send_delete(url, headers, data)


def update_guest_star_slot_settings(
    token: str,
    client_id: str,
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
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
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

    http.send_patch(url, headers, data)
