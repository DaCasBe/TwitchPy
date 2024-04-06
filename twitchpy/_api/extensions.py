from .._utils import http
from ..dataclasses import Extension


def get_extension_transactions(
    token: str,
    client_id: str,
    extension_id: str,
    transaction_ids: list[str] | None = None,
    first: int = 20,
) -> list[dict]:
    url = "https://api.twitch.tv/helix/extensions/transactions"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {}
    params["extension_id"] = extension_id

    if transaction_ids is not None and len(transaction_ids) > 0:
        params["id"] = transaction_ids

    return http.send_get_with_pagination(url, headers, params, first, 100)


def get_extension_configuration_segment(
    token: str, client_id: str, broadcaster_id: str, extension_id: str, segment: str
) -> dict:
    url = "https://api.twitch.tv/helix/extensions/configurations"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {
        "broadcaster_id": broadcaster_id,
        "extension_id": extension_id,
        "segment": segment,
    }

    return http.send_get(url, headers, params)[0]


def set_extension_configuration_segment(
    token: str,
    client_id: str,
    extension_id: str,
    segment: str,
    broadcaster_id: str = "",
    content: str = "",
    version: str = "",
) -> None:
    url = "https://api.twitch.tv/helix/extensions/configurations"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    data = {"extension_id": extension_id, "segment": segment}

    if broadcaster_id != "":
        data["broadcaster_id"] = broadcaster_id

    if content != "":
        data["content"] = content

    if version != "":
        data["version"] = version

    http.send_put(url, headers, data)


def set_extension_required_configuration(
    token: str,
    client_id: str,
    broadcaster_id: str,
    extension_id: str,
    extension_version: str,
    configuration_version: str,
) -> None:
    url = "https://api.twitch.tv/helix/extensions/required_configuration"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    data = {
        "broadcaster_id": broadcaster_id,
        "extension_id": extension_id,
        "extension_version": extension_version,
        "configuration_version": configuration_version,
    }

    http.send_put(url, headers, data)


def send_extension_pubsub_message(
    token: str,
    client_id: str,
    target: list[str],
    broadcaster_id: str,
    is_global_broadcast: bool,
    message: str,
) -> None:
    url = "https://api.twitch.tv/helix/extensions/pubsub"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    payload = {
        "target": target,
        "broadcaster_id": broadcaster_id,
        "is_global_broadcast": is_global_broadcast,
        "message": message,
    }

    http.send_post(url, headers, payload)


def get_extension_live_channels(
    token: str, client_id: str, extension_id: str, first: int = 20
) -> list[dict]:
    url = "https://api.twitch.tv/helix/extensions/live"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": {client_id},
    }
    params = {"extension_id": extension_id}

    return http.send_get_with_pagination(url, headers, params, first, 100)


def get_extension_secrets(token: str, client_id: str) -> list[dict]:
    url = "https://api.twitch.tv/helix/extensions/jwt/secrets"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }

    return http.send_get(url, headers, {})


def create_extension_secret(token: str, client_id: str, delay: int = 300) -> list[dict]:
    url = "https://api.twitch.tv/helix/extensions/jwt/secrets"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    payload = {}

    if delay != 300:
        payload["delay"] = delay

    return http.send_post_get_result(url, headers, payload)


def send_extension_chat_message(
    token: str,
    client_id: str,
    broadcaster_id: str,
    text: str,
    extension_id: str,
    extension_version: str,
) -> None:
    url = "https://api.twitch.tv/helix/extensions/chat"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    payload = {
        "broadcaster_id": broadcaster_id,
        "text": text,
        "extension_id": extension_id,
        "extension_version": extension_version,
    }

    http.send_post(url, headers, payload)


def get_extensions(
    token: str, client_id: str, extension_id: str, extension_version: str = ""
) -> Extension:
    url = "https://api.twitch.tv/helix/extensions"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {"extension_id": extension_id}

    if extension_version != "":
        params["extension_version"] = extension_version

    extension = http.send_get(url, headers, params)[0]

    return Extension(
        extension["author_name"],
        extension["bits_enables"],
        extension["can_install"],
        extension["configuration_location"],
        extension["description"],
        extension["eula_tos_url"],
        extension["has_chat_support"],
        extension["icon_url"],
        extension["icon_urls"],
        extension["id"],
        extension["name"],
        extension["privacy_policy_url"],
        extension["request_identity_link"],
        extension["screenshot_urls"],
        extension["state"],
        extension["subscriptions_support_level"],
        extension["summary"],
        extension["support_email"],
        extension["version"],
        extension["viewer_summary"],
        extension["views"],
        extension["allowlisted_config_urls"],
        extension["allowlisted_panel_urls"],
    )


def get_released_extensions(
    token: str, client_id: str, extension_id: str, extension_version: str = ""
) -> Extension:
    url = "https://api.twitch.tv/helix/extensions/released"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {"extension_id": extension_id}

    if extension_version != "":
        params["extension_version"] = extension_version

    extension = http.send_get(url, headers, params)[0]

    return Extension(
        extension["author_name"],
        extension["bits_enables"],
        extension["can_install"],
        extension["configuration_location"],
        extension["description"],
        extension["eula_tos_url"],
        extension["has_chat_support"],
        extension["icon_url"],
        extension["icon_urls"],
        extension["id"],
        extension["name"],
        extension["privacy_policy_url"],
        extension["request_identity_link"],
        extension["screenshot_urls"],
        extension["state"],
        extension["subscriptions_support_level"],
        extension["summary"],
        extension["support_email"],
        extension["version"],
        extension["viewer_summary"],
        extension["views"],
        extension["allowlisted_config_urls"],
        extension["allowlisted_panel_urls"],
    )


def get_extension_bits_products(
    token: str, extension_client_id: str, should_include_all: bool = False
) -> list[dict]:
    url = "https://api.twitch.tv/helix/bits/extensions"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": extension_client_id,
    }
    params = {}

    if should_include_all is not False:
        params["should_include_all"] = should_include_all

    return http.send_get(url, headers, params)


def update_extension_bits_product(
    token: str,
    extension_client_id: str,
    sku: str,
    cost: dict,
    display_name: str,
    in_development: bool = False,
    expiration: str = "",
    is_broadcast: bool = False,
) -> list[dict]:
    url = "https://api.twitch.tv/helix/bits/extensions"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": extension_client_id,
    }
    data = {"sku": sku, "cost": cost, "display_name": display_name}

    if in_development is not False:
        data["in_development"] = in_development

    if expiration != "":
        data["expiration"] = expiration

    if is_broadcast is not False:
        data["is_broadcast"] = is_broadcast

    return http.send_put_get_result(url, headers, data)
