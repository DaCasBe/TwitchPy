from .._utils import http
from ..dataclasses import Redemption, Reward

ENDPOINT_CUSTOM_REWARDS = "https://api.twitch.tv/helix/channel_points/custom_rewards"


def create_custom_reward(
    token: str,
    client_id: str,
    broadcaster_id: str,
    title: str,
    cost: int,
    prompt: str = "",
    is_enabled: bool = True,
    background_color: str = "",
    is_user_input_required: bool = False,
    is_max_per_stream_enabled: bool = False,
    max_per_stream: int | None = None,
    is_max_per_user_per_stream_enabled: bool = False,
    max_per_user_per_stream: int | None = None,
    is_global_cooldown_enabled: bool = False,
    global_cooldown_seconds: int | None = None,
    should_redemptions_skip_request_queue: bool | None = False,
) -> Reward:
    url = ENDPOINT_CUSTOM_REWARDS
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {"broadcaster_id": broadcaster_id, "title": title, "cost": cost}

    if prompt != "":
        params["prompt"] = prompt

    if is_enabled is not True:
        params["is_enabled"] = is_enabled

    if background_color != "":
        params["background_color"] = background_color

    if is_user_input_required is not False:
        params["is_user_input_required"] = is_user_input_required

    if is_max_per_stream_enabled is not False:
        params["is_max_per_stream_enabled"] = is_max_per_stream_enabled

    if max_per_stream is not None:
        params["max_per_stream"] = max_per_stream

    if is_max_per_user_per_stream_enabled is not False:
        params["is_max_per_user_per_stream_enabled"] = (
            is_max_per_user_per_stream_enabled
        )

    if max_per_user_per_stream is not None:
        params["max_per_user_per_stream"] = max_per_user_per_stream

    if is_global_cooldown_enabled is not False:
        params["is_global_cooldown_enabled"] = is_global_cooldown_enabled

    if global_cooldown_seconds is not None:
        params["global_cooldown_seconds"] = global_cooldown_seconds

    if should_redemptions_skip_request_queue is not False:
        params["should_redemptions_skip_request_queue"] = (
            should_redemptions_skip_request_queue
        )

    reward = http.send_get(url, headers, params)[0]

    return Reward(
        reward["broadcaster_name"],
        reward["broadcaster_id"],
        reward["id"],
        image=reward["image"],
        background_color=reward["background_color"],
        is_enabled=reward["is_enabled"],
        cost=reward["cost"],
        title=reward["title"],
        prompt=reward["prompt"],
        is_user_input_required=reward["is_user_input_required"],
        max_per_stream_setting=reward["max_per_stream_setting"],
        max_per_user_per_stream_setting=reward["max_per_user_per_stream_setting"],
        global_cooldown_setting=reward["global_cooldown_setting"],
        is_paused=reward["is_paused"],
        is_in_stock=reward["is_in_stock"],
        default_image=reward["default_image"],
        should_redemptions_skip_request_queue=reward[
            "should_redemptions_skip_request_queue"
        ],
        redemptions_redeemed_current_stream=reward[
            "redemptions_redeemed_current_stream"
        ],
        cooldown_expires_at=reward["cooldown_expires_at"],
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
    params = {}
    params["broadcaster_id"] = broadcaster_id

    if reward_ids is not None and len(reward_ids) > 0:
        params["id"] = reward_ids

    if only_manageable_rewards is not False:
        params["only_manageable_rewards"] = only_manageable_rewards

    rewards = http.send_get(url, headers, params)

    return [
        Reward(
            reward["broadcaster_name"],
            reward["broadcaster_id"],
            reward["id"],
            image=reward["image"],
            background_color=reward["background_color"],
            is_enabled=reward["is_enabled"],
            cost=reward["cost"],
            title=reward["title"],
            prompt=reward["prompt"],
            is_user_input_required=reward["is_user_input_required"],
            max_per_stream_setting=reward["max_per_stream_setting"],
            max_per_user_per_stream_setting=reward["max_per_user_per_stream_setting"],
            global_cooldown_setting=reward["global_cooldown_setting"],
            is_paused=reward["is_paused"],
            is_in_stock=reward["is_in_stock"],
            default_image=reward["default_image"],
            should_redemptions_skip_request_queue=reward[
                "should_redemptions_skip_request_queue"
            ],
            redemptions_redeemed_current_stream=reward[
                "redemptions_redeemed_current_stream"
            ],
            cooldown_expires_at=reward["cooldown_expires_at"],
        )
        for reward in rewards
    ]


def get_custom_reward_redemption(
    token: str,
    client_id: str,
    broadcaster_id: str,
    reward_id: str,
    redemption_ids: list[str] | None = None,
    status: str = "",
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

    if redemption_ids is not None and len(redemption_ids) > 0:
        params["id"] = redemption_ids

    if status != "":
        params["status"] = status

    if sort != "OLDEST":
        params["sort"] = sort

    redemptions = http.send_get_with_pagination(url, headers, params, first, 50)

    return [
        Redemption(
            redemption["broadcaster_name"],
            redemption["broadcaster_id"],
            redemption["id"],
            redemption["user_id"],
            redemption["user_name"],
            redemption["user_input"],
            redemption["status"],
            redemption["redeemed_at"],
            Reward(
                redemption["broadcaster_name"],
                redemption["broadcaster_id"],
                redemption["reward"]["id"],
                cost=redemption["reward"]["cost"],
                title=redemption["reward"]["title"],
                prompt=redemption["reward"]["prompt"],
            ),
        )
        for redemption in redemptions
    ]


def update_custom_reward(
    token: str,
    client_id: str,
    broadcaster_id: str,
    reward_id: str,
    title: str = "",
    prompt: str = "",
    cost: int | None = None,
    background_color: str = "",
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

    if title != "":
        data["title"] = title

    if prompt != "":
        data["prompt"] = prompt

    if cost is not None:
        data["cost"] = cost

    if background_color != "":
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
        reward["broadcaster_name"],
        reward["broadcaster_id"],
        reward["id"],
        image=reward["image"],
        background_color=reward["background_color"],
        is_enabled=reward["is_enabled"],
        cost=reward["cost"],
        title=reward["title"],
        prompt=reward["prompt"],
        is_user_input_required=reward["is_user_input_required"],
        max_per_stream_setting=reward["max_per_stream_setting"],
        max_per_user_per_stream_setting=reward["max_per_user_per_stream_setting"],
        global_cooldown_setting=reward["global_cooldown_setting"],
        is_paused=reward["is_paused"],
        is_in_stock=reward["is_in_stock"],
        default_image=reward["default_image"],
        should_redemptions_skip_request_queue=reward[
            "should_redemptions_skip_request_queue"
        ],
        redemptions_redeemed_current_stream=reward[
            "redemptions_redeemed_current_stream"
        ],
        cooldown_expires_at=reward["cooldown_expires_at"],
    )


def update_redemption_status(
    token: str,
    client_id: str,
    redemption_id: list[str],
    broadcaster_id: str,
    reward_id: str,
    status: str = "",
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

    if status != "":
        data["status"] = status

    redemptions = http.send_patch_get_result(url, headers, data)

    return [
        Redemption(
            redemption["broadcaster_name"],
            redemption["broadcaster_id"],
            redemption["id"],
            redemption["user_id"],
            redemption["user_name"],
            redemption["user_input"],
            redemption["status"],
            redemption["redeemed_at"],
            Reward(
                redemption["broadcaster_name"],
                redemption["broadcaster_id"],
                redemption["reward"]["id"],
                cost=redemption["reward"]["cost"],
                title=redemption["reward"]["title"],
                prompt=redemption["reward"]["prompt"],
            ),
        )
        for redemption in redemptions
    ]
