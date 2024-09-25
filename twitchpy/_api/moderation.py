from datetime import datetime

from .._utils import date, http
from ..dataclasses import (
    AutoModSettings,
    BannedUser,
    BlockedTerm,
    Channel,
    ChatterWarning,
    ShieldModeStatus,
    UnbanRequest,
    User,
)

ENDPOINT_BLOCKED_TERMS = "https://api.twitch.tv/helix/moderation/blocked_terms"
ENDPOINT_MODERATORS = "https://api.twitch.tv/helix/moderation/moderators"

CONTENT_TYPE_APPLICATION_JSON = "application/json"


def check_automod_status(
    token: str, client_id: str, broadcaster_id: str, data: list[tuple[str, str]]
) -> list[tuple[str, bool]]:
    url = "https://api.twitch.tv/helix/moderation/enforcements/status"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    payload = {
        "broadcaster_id": broadcaster_id,
        "data": data,
    }

    messages_status = http.send_post_get_result(url, headers, payload)

    return [
        (message_status["msg_id"], message_status["is_permited"])
        for message_status in messages_status
    ]


def manage_held_automod_messages(
    token: str, client_id: str, user_id: str, msg_id: str, action: str
) -> None:
    url = "https://api.twitch.tv/helix/moderation/automod/message"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    payload = {"user_id": user_id, "msg_id": msg_id, "action": action}

    http.send_post(url, headers, payload)


def get_automod_settings(
    token: str, client_id: str, broadcaster_id: str, moderator_id: str
) -> AutoModSettings:
    url = "https://api.twitch.tv/helix/moderation/automod/settings"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {"broadcaster_id": broadcaster_id, "moderator_id": moderator_id}

    settings = http.send_get(url, headers, params)[0]

    return AutoModSettings(
        settings["broadcaster_id"],
        settings["moderator_id"],
        settings["overall_level"],
        settings["disability"],
        settings["aggression"],
        settings["sexuality_sex_or_gender"],
        settings["misogyny"],
        settings["bullying"],
        settings["swearing"],
        settings["race_ethnicity_or_religion"],
        settings["sex_based_terms"],
    )


def update_automod_settings(
    token: str,
    client_id: str,
    broadcaster_id: str,
    moderator_id: str,
    aggression: int | None = None,
    bullying: int | None = None,
    disability: int | None = None,
    misogyny: int | None = None,
    overall_level: int | None = None,
    race_ethnicity_or_religion: int | None = None,
    sex_based_terms: int | None = None,
    sexuality_sex_or_gender: int | None = None,
    swearing: int | None = None,
) -> AutoModSettings:
    url = "https://api.twitch.tv/helix/moderation/automod/settings"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
        "Content-Type": CONTENT_TYPE_APPLICATION_JSON,
    }
    data = {}
    data["broadcaster_id"] = broadcaster_id
    data["moderator_id"] = moderator_id

    if aggression is not None:
        data["aggression"] = aggression

    if bullying is not None:
        data["bullying"] = bullying

    if disability is not None:
        data["disability"] = disability

    if misogyny is not None:
        data["misogyny"] = misogyny

    if overall_level is not None:
        data["overall_level"] = overall_level

    if race_ethnicity_or_religion is not None:
        data["race_ethnicity_or_religion"] = race_ethnicity_or_religion

    if sex_based_terms is not None:
        data["sex_based_terms"] = sex_based_terms

    if sexuality_sex_or_gender is not None:
        data["sexuality_sex_or_gender"] = sexuality_sex_or_gender

    if swearing is not None:
        data["swearing"] = swearing

    settings = http.send_put_get_result(url, headers, data)[0]

    return AutoModSettings(
        settings["broadcaster_id"],
        settings["moderator_id"],
        settings["overall_level"],
        settings["disability"],
        settings["aggression"],
        settings["sexuality_sex_or_gender"],
        settings["misogyny"],
        settings["bullying"],
        settings["swearing"],
        settings["race_ethnicity_or_religion"],
        settings["sex_based_terms"],
    )


def get_banned_users(
    token: str,
    client_id: str,
    broadcaster_id: str,
    user_id: list[str] | None = None,
    first: int = 20,
) -> list[BannedUser]:
    url = "https://api.twitch.tv/helix/moderation/banned"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {}
    params["broadcaster_id"] = broadcaster_id

    if user_id is not None and len(user_id) > 0:
        params["user_id"] = user_id

    if first != 20:
        params["first"] = first

    users = http.send_get_with_pagination(url, headers, params, first, 100)

    return [
        BannedUser(
            User(user["user_id"], user["user_login"], user["user_name"]),
            datetime.strptime(user["expires_at"], date.RFC3339_FORMAT),
            datetime.strptime(user["created_at"], date.RFC3339_FORMAT),
            user["reason"],
            User(user["moderator_id"], user["moderator_login"], user["moderator_name"]),
        )
        for user in users
    ]


def ban_user(
    token: str,
    client_id: str,
    broadcaster_id: str,
    moderator_id: str,
    reason: str,
    user_id: str,
    duration: int | None = None,
) -> dict:
    url = "https://api.twitch.tv/helix/moderation/bans"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    payload = {}
    payload["broadcaster_id"] = broadcaster_id
    payload["moderator_id"] = moderator_id

    data = {}
    data["reason"] = reason
    data["user_id"] = user_id

    if duration is not None:
        data["duration"] = duration

    payload["data"] = data

    return http.send_post_get_result(url, headers, payload)[0]


def unban_user(
    token: str, client_id: str, broadcaster_id: str, moderator_id: str, user_id: str
) -> None:
    url = "https://api.twitch.tv/helix/moderation/bans"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    data = {
        "broadcaster_id": broadcaster_id,
        "moderator_id": moderator_id,
        "user_id": user_id,
    }

    http.send_delete(url, headers, data)


def get_unban_requests(
    token: str,
    client_id: str,
    broadcaster_id: str,
    moderator_id: str,
    status: str,
    user_id: str | None = None,
    first: int = 20,
) -> list[UnbanRequest]:
    url = "https://api.twitch.tv/helix/moderation/unban_requests"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {
        "broadcaster_id": broadcaster_id,
        "moderator_id": moderator_id,
        "status": status,
    }

    if user_id is not None:
        params["user_id"] = user_id

    requests = http.send_get_with_pagination(url, headers, params, first, 100)

    return [
        UnbanRequest(
            request["id"],
            Channel(
                User(
                    request["broadcaster_id"],
                    request["broadcaster_login"],
                    request["broadcaster_name"],
                )
            ),
            User(
                request["moderator_id"],
                request["moderator_login"],
                request["moderator_name"],
            ),
            User(request["user_id"], request["user_login"], request["user_name"]),
            request["text"],
            request["status"],
            datetime.strptime(request["created_at"], date.RFC3339_FORMAT),
            datetime.strptime(request["resolved_at"], date.RFC3339_FORMAT),
            request["resolution_text"],
        )
        for request in requests
    ]


def resolve_unban_requests(
    token: str,
    client_id: str,
    broadcaster_id: str,
    moderator_id: str,
    unban_request_id: str,
    status: str,
    resolution_text: str | None = None,
) -> UnbanRequest:
    url = "https://api.twitch.tv/helix/moderation/unban_requests"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    data = {
        "broadcaster_id": broadcaster_id,
        "moderator_id": moderator_id,
        "unban_request_id": unban_request_id,
        "status": status,
    }

    if resolution_text is not None:
        data["resolution_text"] = resolution_text

    request = http.send_patch_get_result(url, headers, data)[0]

    return UnbanRequest(
        request["id"],
        Channel(
            User(
                request["broadcaster_id"],
                request["broadcaster_login"],
                request["broadcaster_name"],
            )
        ),
        User(
            request["moderator_id"],
            request["moderator_login"],
            request["moderator_name"],
        ),
        User(request["user_id"], request["user_login"], request["user_name"]),
        request["text"],
        request["status"],
        datetime.strptime(request["created_at"], date.RFC3339_FORMAT),
        datetime.strptime(request["resolved_at"], date.RFC3339_FORMAT),
        request["resolution_text"],
    )


def get_blocked_terms(
    token: str, client_id: str, broadcaster_id: str, moderator_id: str, first: int = 20
) -> list[BlockedTerm]:
    url = ENDPOINT_BLOCKED_TERMS
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {}
    params["broadcaster_id"] = broadcaster_id
    params["moderator_id"] = moderator_id

    if first != 20:
        params["first"] = first

    terms = http.send_get_with_pagination(url, headers, params, first, 100)

    return [
        BlockedTerm(
            term["broadcaster_id"],
            term["moderator_id"],
            term["id"],
            term["text"],
            datetime.strptime(term["created_at"], date.RFC3339_FORMAT),
            datetime.strptime(term["updated_at"], date.RFC3339_FORMAT),
            datetime.strptime(term["expires_at"], date.RFC3339_FORMAT),
        )
        for term in terms
    ]


def add_blocked_term(
    token: str, client_id: str, broadcaster_id: str, moderator_id: str, text: str
) -> BlockedTerm:
    url = ENDPOINT_BLOCKED_TERMS
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
        "Content-Type": CONTENT_TYPE_APPLICATION_JSON,
    }
    payload = {
        "broadcaster_id": broadcaster_id,
        "moderator_id": moderator_id,
        "text": text,
    }

    term = http.send_post_get_result(url, headers, payload)[0]

    return BlockedTerm(
        term["broadcaster_id"],
        term["moderator_id"],
        term["id"],
        term["text"],
        datetime.strptime(term["created_at"], date.RFC3339_FORMAT),
        datetime.strptime(term["updated_at"], date.RFC3339_FORMAT),
        datetime.strptime(term["expires_at"], date.RFC3339_FORMAT),
    )


def remove_blocked_term(
    token: str,
    client_id: str,
    broadcaster_id: str,
    blocked_term_id: str,
    moderator_id: str,
) -> None:
    url = ENDPOINT_BLOCKED_TERMS
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    data = {
        "broadcaster_id": broadcaster_id,
        "id": blocked_term_id,
        "moderator_id": moderator_id,
    }

    http.send_delete(url, headers, data)


def delete_chat_messages(
    token: str,
    client_id: str,
    broadcaster_id: str,
    moderator_id: str,
    message_id: str | None = None,
) -> None:
    url = "https://api.twitch.tv/helix/moderation/chat"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    data = {"broadcaster_id": broadcaster_id, "moderator_id": moderator_id}

    if message_id is not None:
        data["message_id"] = message_id

    http.send_delete(url, headers, data)


def get_moderated_channels(
    token: str, client_id: str, user_id: str, first: int = 20
) -> list[Channel]:
    url = "https://api.twitch.tv/helix/moderation/channels"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {"user_id": user_id}

    channels = http.send_get_with_pagination(url, headers, params, first, 100)

    return [
        Channel(
            User(
                channel["broadcaster_id"],
                channel["broadcaster_login"],
                channel["broadcaster_name"],
            )
        )
        for channel in channels
    ]


def get_moderators(
    token: str,
    client_id: str,
    broadcaster_id: str,
    user_id: list[str] | None = None,
    first: int = 20,
) -> list[User]:
    url = ENDPOINT_MODERATORS
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {}
    params["broadcaster_id"] = broadcaster_id

    if user_id is not None and len(user_id) > 0:
        params["user_id"] = user_id

    users = http.send_get_with_pagination(url, headers, params, first, 100)

    return [
        User(user["user_id"], user["user_login"], user["user_name"]) for user in users
    ]


def add_channel_moderator(
    token: str, client_id: str, broadcaster_id: str, user_id: str
) -> None:
    url = ENDPOINT_MODERATORS
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    payload = {"broadcaster_id": broadcaster_id, "user_id": user_id}

    http.send_post(url, headers, payload)


def remove_channel_moderator(
    token: str, client_id: str, broadcaster_id: str, user_id: str
) -> None:
    url = ENDPOINT_MODERATORS
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    data = {"broadcaster_id": broadcaster_id, "user_id": user_id}

    http.send_delete(url, headers, data)


def update_shield_mode_status(
    token: str, client_id: str, broadcaster_id: str, moderator_id: str, is_active: bool
) -> ShieldModeStatus:
    url = "https://api.twitch.tv/helix/moderation/shield_mode"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
        "Content-Type": CONTENT_TYPE_APPLICATION_JSON,
    }
    data = {
        "broadcaster_id": broadcaster_id,
        "moderator_id": moderator_id,
        "is_active": is_active,
    }

    shield_mode_status = http.send_put_get_result(url, headers, data)[0]

    return ShieldModeStatus(
        shield_mode_status["is_active"],
        User(
            shield_mode_status["moderator_id"],
            shield_mode_status["moderator_login"],
            shield_mode_status["moderator_name"],
        ),
        datetime.strptime(shield_mode_status["last_activated_at"], date.RFC3339_FORMAT),
    )


def get_shield_mode_status(
    token: str, client_id: str, broadcaster_id: str, moderator_id: str
) -> ShieldModeStatus:
    url = "https://api.twitch.tv/helix/moderation/shield_mode"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {"broadcaster_id": broadcaster_id, "moderator_id": moderator_id}

    shield_mode_status = http.send_get(url, headers, params)[0]

    return ShieldModeStatus(
        shield_mode_status["is_active"],
        User(
            shield_mode_status["moderator_id"],
            shield_mode_status["moderator_login"],
            shield_mode_status["moderator_name"],
        ),
        datetime.strptime(shield_mode_status["last_activated_at"], date.RFC3339_FORMAT),
    )


def warn_chat_user(
    token: str,
    client_id: str,
    broadcaster_id: str,
    moderator_id: str,
    user_id: str,
    reason: str,
) -> ChatterWarning:
    url = "https://api.twitch.tv/helix/moderation/warnings"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
        "Content-Type": CONTENT_TYPE_APPLICATION_JSON,
    }
    payload = {
        "broadcaster_id": broadcaster_id,
        "moderator_id": moderator_id,
        "data": {"user_id": user_id, "reason": reason},
    }

    warning = http.send_post_get_result(url, headers, payload)[0]

    return ChatterWarning(
        warning["broadcaster_id"],
        warning["user_id"],
        warning["moderator_id"],
        warning["reason"],
    )
