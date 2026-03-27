from datetime import datetime

from .._utils import date, http
from ..dataclasses import (Channel, Extension, ExtensionConfigurationSegment,
                           ExtensionSecret, ExtensionTransaction, Game,
                           Product, ProductCost, User)


async def get_extension_transactions(
    token: str,
    client_id: str,
    extension_id: str,
    transaction_ids: list[str] | None = None,
    first: int = 20,
) -> list[ExtensionTransaction]:
    url = "https://api.twitch.tv/helix/extensions/transactions"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {}
    params["extension_id"] = extension_id

    if transaction_ids is not None and len(transaction_ids) > 0:
        params["id"] = transaction_ids

    transactions = await http.send_get_with_pagination(url, headers, params, first, 100)

    return [
        ExtensionTransaction(
            transaction["id"],
            datetime.strptime(transaction["timestamp"], date.RFC3339_FORMAT),
            Channel(
                User(
                    transaction["broadcaster_id"],
                    transaction["broadcaster_login"],
                    transaction["broadcaster_name"],
                )
            ),
            User(
                transaction["user_id"],
                transaction["user_login"],
                transaction["user_name"],
            ),
            transaction["product_type"],
            Product(
                transaction["product_data"]["sku"],
                ProductCost(
                    transaction["product_data"]["cost"]["amount"],
                    transaction["product_data"]["cost"]["type"],
                ),
                transaction["product_data"]["inDevelopment"],
                transaction["product_data"]["displayName"],
                transaction["product_data"]["expiration"],
                transaction["product_data"]["broadcast"],
                transaction["product_data"]["domain"],
            ),
        )
        for transaction in transactions
    ]


async def get_extension_configuration_segment(
    token: str, client_id: str, broadcaster_id: str, extension_id: str, segment: str
) -> ExtensionConfigurationSegment:
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

    configuration_segment = (await http.send_get(url, headers, params))[0]

    return ExtensionConfigurationSegment(
        configuration_segment["segment"],
        configuration_segment["broadcaster_id"],
        configuration_segment["content"],
        configuration_segment["version"],
    )


async def set_extension_configuration_segment(
    token: str,
    client_id: str,
    extension_id: str,
    segment: str,
    broadcaster_id: str | None = None,
    content: str | None = None,
    version: str | None = None,
) -> None:
    url = "https://api.twitch.tv/helix/extensions/configurations"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    data = {"extension_id": extension_id, "segment": segment}

    if broadcaster_id is not None:
        data["broadcaster_id"] = broadcaster_id

    if content is not None:
        data["content"] = content

    if version is not None:
        data["version"] = version

    await http.send_put(url, headers, data)


async def set_extension_required_configuration(
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

    await http.send_put(url, headers, data)


async def send_extension_pubsub_message(
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

    await http.send_post(url, headers, payload)


async def get_extension_live_channels(
    token: str, client_id: str, extension_id: str, first: int = 20
) -> list[Channel]:
    url = "https://api.twitch.tv/helix/extensions/live"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": {client_id},
    }
    params = {"extension_id": extension_id}

    channels = await http.send_get_with_pagination(url, headers, params, first, 100)

    return [
        Channel(
            User(
                channel["broadcaster_id"],
                channel["broadcaster_name"].lower(),
                channel["broadcaster_name"],
            ),
            game=Game(channel["game_id"], channel["game_name"]),
            title=channel["title"],
        )
        for channel in channels
    ]


async def get_extension_secrets(
    token: str, client_id: str
) -> list[tuple[str, list[ExtensionSecret]]]:
    url = "https://api.twitch.tv/helix/extensions/jwt/secrets"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }

    extension_secrets = await http.send_get(url, headers, {})

    return [
        (
            extension_secret["format_version"],
            [
                ExtensionSecret(
                    secret["content"], secret["active_at"], secret["expires_at"]
                )
                for secret in extension_secret["secrets"]
            ],
        )
        for extension_secret in extension_secrets
    ]


async def create_extension_secret(
    token: str, client_id: str, delay: int = 300
) -> list[tuple[str, list[ExtensionSecret]]]:
    url = "https://api.twitch.tv/helix/extensions/jwt/secrets"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    payload = {"delay": delay}

    extension_secrets = await http.send_post_get_result(url, headers, payload)

    return [
        (
            extension_secret["format_version"],
            [
                ExtensionSecret(
                    secret["content"], secret["active_at"], secret["expires_at"]
                )
                for secret in extension_secret["secrets"]
            ],
        )
        for extension_secret in extension_secrets
    ]


async def send_extension_chat_message(
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

    await http.send_post(url, headers, payload)


async def get_extensions(
    token: str, client_id: str, extension_id: str, extension_version: str | None = None
) -> Extension:
    url = "https://api.twitch.tv/helix/extensions"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {"extension_id": extension_id}

    if extension_version is not None:
        params["extension_version"] = extension_version

    extension = (await http.send_get(url, headers, params))[0]

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


async def get_released_extensions(
    token: str, client_id: str, extension_id: str, extension_version: str | None = None
) -> Extension:
    url = "https://api.twitch.tv/helix/extensions/released"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {"extension_id": extension_id}

    if extension_version is not None:
        params["extension_version"] = extension_version

    extension = (await http.send_get(url, headers, params))[0]

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


async def get_extension_bits_products(
    token: str, extension_client_id: str, should_include_all: bool = False
) -> list[Product]:
    url = "https://api.twitch.tv/helix/bits/extensions"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": extension_client_id,
    }
    params = {"should_include_all": should_include_all}

    products = await http.send_get(url, headers, params)

    return [
        Product(
            product["sku"],
            ProductCost(product["cost"]["amount"], product["cost"]["type"]),
            product["in_development"],
            product["display_name"],
            product["expiration"],
            product["is_broadcast"],
        )
        for product in products
    ]


async def update_extension_bits_product(
    token: str,
    extension_client_id: str,
    sku: str,
    cost: dict,
    display_name: str,
    in_development: bool | None = None,
    expiration: str | None = None,
    is_broadcast: bool | None = None,
) -> list[Product]:
    url = "https://api.twitch.tv/helix/bits/extensions"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": extension_client_id,
    }
    data = {"sku": sku, "cost": cost, "display_name": display_name}

    if in_development is not None:
        data["in_development"] = in_development

    if expiration is not None:
        data["expiration"] = expiration

    if is_broadcast is not None:
        data["is_broadcast"] = is_broadcast

    products = await http.send_put_get_result(url, headers, data)

    return [
        Product(
            product["sku"],
            ProductCost(product["cost"]["amount"], product["cost"]["type"]),
            product["in_development"],
            product["display_name"],
            product["expiration"],
            product["is_broadcast"],
        )
        for product in products
    ]
