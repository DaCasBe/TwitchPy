from datetime import datetime

from .._utils import date, http
from ..dataclasses import Channel, Redemption, Reward, User

ENDPOINT_CUSTOM_REWARDS = "https://api.twitch.tv/helix/channel_points/custom_rewards"


def create_custom_reward(
    token: str,
    client_id: str,
    broadcaster_id: str,
    title: str,
    cost: int,
    prompt: str | None = None,
    is_enabled: bool = True,
    background_color: str | None = None,
    is_user_input_required: bool = False,
    is_max_per_stream_enabled: bool = False,
    max_per_stream: int | None = None,
    is_max_per_user_per_stream_enabled: bool = False,
    max_per_user_per_stream: int | None = None,
    is_global_cooldown_enabled: bool = False,
    global_cooldown_seconds: int | None = None,
    should_redemptions_skip_request_queue: bool = False,
) -> Reward:
    url = ENDPOINT_CUSTOM_REWARDS
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {
        "broadcaster_id": broadcaster_id,
        "title": title,
        "cost": cost,
        "is_enabled": is_enabled,
        "is_user_input_required": is_user_input_required,
        "is_max_per_stream_enabled": is_max_per_stream_enabled,
        "is_max_per_user_per_stream_enabled": is_max_per_user_per_stream_enabled,
        "is_global_cooldown_enabled": is_global_cooldown_enabled,
        "should_redemptions_skip_request_queue": should_redemptions_skip_request_queue,
    }

    if prompt is not None:
        params["prompt"] = prompt

    if background_color is not None:
        params["background_color"] = background_color

    if max_per_stream is not None:
        params["max_per_stream"] = max_per_stream

    if max_per_user_per_stream is not None:
        params["max_per_user_per_stream"] = max_per_user_per_stream

    if global_cooldown_seconds is not None:
        params["global_cooldown_seconds"] = global_cooldown_seconds

    reward = http.send_get(url, headers, params)[0]

    return Reward(
        Channel(
            User(
                reward["broadcaster_id"],
                reward["broadcaster_login"],
                reward["broadcaster_name"],
            )
        ),
        reward["id"],
        reward["title"],
        reward["prompt"],
        reward["cost"],
        reward["image"],
        reward["default_image"],
        reward["background_color"],
        reward["is_enabled"],
        reward["is_user_input_required"],
        (
            reward["max_per_stream_setting"]["is_enabled"],
            reward["max_per_stream_setting"]["max_per_stream"],
        ),
        (
            reward["max_per_user_per_stream_setting"]["is_enabled"],
            reward["max_per_user_per_stream_setting"]["max_per_user_per_stream"],
        ),
        (
            reward["global_cooldown_setting"]["is_enabled"],
            reward["global_cooldown_setting"]["global_cooldown_seconds"],
        ),
        reward["is_paused"],
        reward["is_in_stock"],
        reward["should_redemptions_skip_request_queue"],
        reward["redemptions_redeemed_current_stream"],
        datetime.strptime(reward["cooldown_expires_at"], date.RFC3339_FORMAT),
    )


def delete_custom_reward(
    token: str, client_id: str, broadcaster_id: str, reward_id: str
) -> None:
    url = ENDPOINT_CUSTOM_REWARDS
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    data = {"broadcaster_id": broadcaster_id, "id": reward_id}

    http.send_delete(url, headers, data)


def get_custom_reward(
    token: str,
    client_id: str,
    broadcaster_id: str,
    reward_ids: list[str] | None = None,
    only_manageable_rewards: bool = False,
) -> list[Reward]:
    url = ENDPOINT_CUSTOM_REWARDS
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {
        "broadcaster_id": broadcaster_id,
        "only_manageable_rewards": only_manageable_rewards,
    }

    if reward_ids is not None and len(reward_ids) > 0:
        params["id"] = reward_ids

    rewards = http.send_get(url, headers, params)

    return [
        Reward(
            Channel(
                User(
                    reward["broadcaster_id"],
                    reward["broadcaster_login"],
                    reward["broadcaster_name"],
                )
            ),
            reward["id"],
            reward["title"],
            reward["prompt"],
            reward["cost"],
            reward["image"],
            reward["default_image"],
            reward["background_color"],
            reward["is_enabled"],
            reward["is_user_input_required"],
            (
                reward["max_per_stream_setting"]["is_enabled"],
                reward["max_per_stream_setting"]["max_per_stream"],
            ),
            (
                reward["max_per_user_per_stream_setting"]["is_enabled"],
                reward["max_per_user_per_stream_setting"]["max_per_user_per_stream"],
            ),
            (
                reward["global_cooldown_setting"]["is_enabled"],
                reward["global_cooldown_setting"]["global_cooldown_seconds"],
            ),
            reward["is_paused"],
            reward["is_in_stock"],
            reward["should_redemptions_skip_request_queue"],
            reward["redemptions_redeemed_current_stream"],
            datetime.strptime(reward["cooldown_expires_at"], date.RFC3339_FORMAT),
        )
        for reward in rewards
    ]


def get_custom_reward_redemption(
    token: str,
    client_id: str,
    broadcaster_id: str,
    reward_id: str,
    redemption_ids: list[str] | None = None,
    status: str | None = None,
    sort: str = "OLDEST",
    first: int = 20,
) -> list[Redemption]:
    url = "https://api.twitch.tv/helix/channel_points/custom_rewards/redemptions"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {}
    params["broadcaster_id"] = broadcaster_id
    params["reward_id"] = reward_id
    params["sort"] = sort

    if redemption_ids is not None and len(redemption_ids) > 0:
        params["id"] = redemption_ids

    if status is not None:
        params["status"] = status

    redemptions = http.send_get_with_pagination(url, headers, params, first, 50)

    return [
        Redemption(
            Channel(
                User(
                    redemption["broadcaster_id"],
                    redemption["broadcaster_login"],
                    redemption["broadcaster_name"],
                )
            ),
            redemption["id"],
            User(
                redemption["user_id"], redemption["user_login"], redemption["user_name"]
            ),
            redemption["user_input"],
            redemption["status"],
            datetime.strptime(redemption["redeemed_at"], date.RFC3339_FORMAT),
            Reward(
                Channel(
                    User(
                        redemption["broadcaster_id"],
                        redemption["broadcaster_login"],
                        redemption["broadcaster_name"],
                    )
                ),
                redemption["reward"]["id"],
                redemption["reward"]["title"],
                redemption["reward"]["prompt"],
                redemption["reward"]["cost"],
            ),
        )
        for redemption in redemptions
    ]


def update_custom_reward(
    token: str,
    client_id: str,
    broadcaster_id: str,
    reward_id: str,
    title: str | None = None,
    prompt: str | None = None,
    cost: int | None = None,
    background_color: str | None = None,
    is_enabled: bool | None = None,
    is_user_input_required: bool | None = None,
    is_max_per_stream_enabled: bool | None = None,
    max_per_stream: int | None = None,
    is_max_per_user_per_stream_enabled: bool | None = None,
    max_per_user_per_stream: int | None = None,
    is_global_cooldown_enabled: bool | None = None,
    global_cooldown_seconds: int | None = None,
    is_paused: bool | None = None,
    should_redemptions_skip_request_queue: bool | None = None,
) -> Reward:
    url = ENDPOINT_CUSTOM_REWARDS
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    data = {}
    data["broadcaster_id"] = broadcaster_id
    data["id"] = reward_id

    if title is not None:
        data["title"] = title

    if prompt is not None:
        data["prompt"] = prompt

    if cost is not None:
        data["cost"] = cost

    if background_color is not None:
        data["background_color"] = background_color

    if is_enabled is not None:
        data["is_enabled"] = is_enabled

    if is_user_input_required is not None:
        data["is_user_input_required"] = is_user_input_required

    if is_max_per_stream_enabled is not None:
        data["is_max_per_stream_enabled"] = is_max_per_stream_enabled

    if max_per_stream is not None:
        data["max_per_stream"] = max_per_stream

    if is_max_per_user_per_stream_enabled is not None:
        data["is_max_per_user_per_stream_enabled"] = is_max_per_user_per_stream_enabled

    if max_per_user_per_stream is not None:
        data["max_per_user_per_stream"] = max_per_user_per_stream

    if is_global_cooldown_enabled is not None:
        data["is_global_cooldown_enabled"] = is_global_cooldown_enabled

    if global_cooldown_seconds is not None:
        data["global_cooldown_seconds"] = global_cooldown_seconds

    if is_paused is not None:
        data["is_paused"] = is_paused

    if should_redemptions_skip_request_queue is not None:
        data["should_redemptions_skip_request_queue"] = (
            should_redemptions_skip_request_queue
        )

    reward = http.send_patch_get_result(url, headers, data)[0]

    return Reward(
        Channel(
            User(
                reward["broadcaster_id"],
                reward["broadcaster_login"],
                reward["broadcaster_name"],
            )
        ),
        reward["id"],
        reward["title"],
        reward["prompt"],
        reward["cost"],
        reward["image"],
        reward["default_image"],
        reward["background_color"],
        reward["is_enabled"],
        reward["is_user_input_required"],
        (
            reward["max_per_stream_setting"]["is_enabled"],
            reward["max_per_stream_setting"]["max_per_stream"],
        ),
        (
            reward["max_per_user_per_stream_setting"]["is_enabled"],
            reward["max_per_user_per_stream_setting"]["max_per_user_per_stream"],
        ),
        (
            reward["global_cooldown_setting"]["is_enabled"],
            reward["global_cooldown_setting"]["global_cooldown_seconds"],
        ),
        reward["is_paused"],
        reward["is_in_stock"],
        reward["should_redemptions_skip_request_queue"],
        reward["redemptions_redeemed_current_stream"],
        datetime.strptime(reward["cooldown_expires_at"], date.RFC3339_FORMAT),
    )


def update_redemption_status(
    token: str,
    client_id: str,
    redemption_id: list[str],
    broadcaster_id: str,
    reward_id: str,
    status: str | None = None,
) -> list[Redemption]:
    url = "https://api.twitch.tv/helix/channel_points/custom_rewards/redemptions"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    data = {
        "id": redemption_id,
        "broadcaster_id": broadcaster_id,
        "reward_id": reward_id,
    }

    if status is not None:
        data["status"] = status

    redemptions = http.send_patch_get_result(url, headers, data)

    return [
        Redemption(
            Channel(
                User(
                    redemption["broadcaster_id"],
                    redemption["broadcaster_login"],
                    redemption["broadcaster_name"],
                )
            ),
            redemption["id"],
            User(
                redemption["user_id"], redemption["user_login"], redemption["user_name"]
            ),
            redemption["user_input"],
            redemption["status"],
            datetime.strptime(redemption["redeemed_at"], date.RFC3339_FORMAT),
            Reward(
                Channel(
                    User(
                        redemption["broadcaster_id"],
                        redemption["broadcaster_login"],
                        redemption["broadcaster_name"],
                    )
                ),
                redemption["reward"]["id"],
                redemption["reward"]["title"],
                redemption["reward"]["prompt"],
                redemption["reward"]["cost"],
            ),
        )
        for redemption in redemptions
    ]
