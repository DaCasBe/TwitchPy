from .._utils import http

ENDPOINT_BLOCKED_TERMS = "https://api.twitch.tv/helix/moderation/blocked_terms"
ENDPOINT_MODERATORS = "https://api.twitch.tv/helix/moderation/moderators"

CONTENT_TYPE_APPLICATION_JSON = "application/json"


def check_automod_status(
    token: str, client_id: str, broadcaster_id: str, msg_id: str, msg_user: str
) -> list[dict]:
    url = "https://api.twitch.tv/helix/moderation/enforcements/status"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    payload = {
        "broadcaster_id": broadcaster_id,
        "data": [{"msg_id": msg_id, "msg_user": msg_user}],
    }

    return http.send_post_get_result(url, headers, payload)


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
) -> dict:
    url = "https://api.twitch.tv/helix/moderation/automod/settings"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {"broadcaster_id": broadcaster_id, "moderator_id": moderator_id}

    return http.send_get(url, headers, params)[0]


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
) -> dict:
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

    return http.send_put_get_result(url, headers, data)[0]


def get_banned_users(
    token: str,
    client_id: str,
    broadcaster_id: str,
    user_id: list[str] | None = None,
    first: int = 20,
) -> list[dict]:
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

    return http.send_get_with_pagination(url, headers, params, first, 100)


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
    user_id: str = "",
    first: int = 20,
) -> list[dict]:
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

    if user_id != "":
        params["user_id"] = user_id

    return http.send_get_with_pagination(url, headers, params, first, 100)


def resolve_unban_requests(
    token: str,
    client_id: str,
    broadcaster_id: str,
    moderator_id: str,
    unban_request_id: str,
    status: str,
    resolution_text: str = "",
) -> list[dict]:
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

    if resolution_text != "":
        data["resolution_text"] = resolution_text

    return http.send_patch_get_result(url, headers, data)


def get_blocked_terms(
    token: str, client_id: str, broadcaster_id: str, moderator_id: str, first: int = 20
) -> list[dict]:
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

    return http.send_get_with_pagination(url, headers, params, first, 100)


def add_blocked_term(
    token: str, client_id: str, broadcaster_id: str, moderator_id: str, text: str
) -> dict:
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

    return http.send_post_get_result(url, headers, payload)[0]


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
    message_id: str = "",
) -> None:
    url = "https://api.twitch.tv/helix/moderation/chat"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    data = {"broadcaster_id": broadcaster_id, "moderator_id": moderator_id}

    if message_id != "":
        data["message_id"] = message_id

    http.send_delete(url, headers, data)


def get_moderated_channels(
    token: str, client_id: str, user_id: str, first: int = 20
) -> list[dict]:
    url = "https://api.twitch.tv/helix/moderation/channels"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {"user_id": user_id}

    return http.send_get_with_pagination(url, headers, params, first, 100)


def get_moderators(
    token: str,
    client_id: str,
    broadcaster_id: str,
    user_id: list[str] | None = None,
    first: int = 20,
) -> list[dict]:
    url = ENDPOINT_MODERATORS
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {}
    params["broadcaster_id"] = broadcaster_id

    if user_id is not None and len(user_id) > 0:
        params["user_id"] = user_id

    return http.send_get_with_pagination(url, headers, params, first, 100)


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
) -> dict:
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

    return http.send_put_get_result(url, headers, data)[0]


def get_shield_mode_status(
    token: str, client_id: str, broadcaster_id: str, moderator_id: str
) -> dict:
    url = "https://api.twitch.tv/helix/moderation/shield_mode"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {"broadcaster_id": broadcaster_id, "moderator_id": moderator_id}

    return http.send_get(url, headers, params)[0]
