from .._utils import http
from ..dataclasses import Channel, Subscription, User


def get_broadcaster_subscriptions(
    token: str,
    client_id: str,
    broadcaster_id: str,
    user_id: list[str] | None = None,
    first: int = 20,
) -> list[Subscription]:
    url = "https://api.twitch.tv/helix/subscriptions"
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

    subscriptions = http.send_get_with_pagination(url, headers, params, first, 100)

    return [
        Subscription(
            Channel(
                User(
                    subscription["broadcaster_id"],
                    subscription["broadcaster_login"],
                    subscription["broadcaster_name"],
                )
            ),
            User(
                subscription["gifter_id"],
                subscription["gifter_login"],
                subscription["gifter_name"],
            ),
            subscription["is_gift"],
            subscription["tier"],
            subscription["plan_name"],
            User(
                subscription["user_id"],
                subscription["user_login"],
                subscription["user_name"],
            ),
        )
        for subscription in subscriptions
    ]


def check_user_subscription(
    token: str, client_id: str, broadcaster_id: str, user_id: str
) -> Subscription:
    url = "https://api.twitch.tv/helix/subscriptions/user"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id,
    }
    params = {"broadcaster_id": broadcaster_id, "user_id": user_id}

    subscription = http.send_get(url, headers, params)[0]

    return Subscription(
        Channel(
            User(
                subscription["broadcaster_id"],
                subscription["broadcaster_login"],
                subscription["broadcaster_name"],
            )
        ),
        User(
            subscription["gifter_id"],
            subscription["gifter_login"],
            subscription["gifter_name"],
        ),
        subscription["is_gift"],
        subscription["tier"],
    )
