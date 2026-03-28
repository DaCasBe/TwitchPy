from datetime import datetime

from .._utils import date, http
from ..dataclasses import (BitsLeaderboardLeader, Channel, Cheermote,
                           CheermoteTier, ExtensionTransaction, Product,
                           ProductCost, User)


class BitsAPI:
    def __init__(self, access_token: str, client_id: str):
        self._access_token = access_token
        self._client_id = client_id

    async def get_bits_leaderboard(
        self,
        count: int = 10,
        period: str = "all",
        started_at: datetime | None = None,
        user_id: str | None = None,
    ) -> list[BitsLeaderboardLeader]:
        url = "https://api.twitch.tv/helix/bits/leaderboard"
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Client-Id": self._client_id,
        }
        params = {"count": count, "period": period}

        if started_at is not None:
            params["started_at"] = started_at

        if user_id is not None:
            params["user_id"] = user_id

        leaderboard = await http.send_get(url, headers, params)

        return [
            BitsLeaderboardLeader(
                User(leader["user_id"], leader["user_login"], leader["user_name"]),
                leader["rank"],
                leader["score"],
            )
            for leader in leaderboard
        ]

    async def get_cheermotes(
        self, broadcaster_id: str | None = None
    ) -> list[Cheermote]:
        url = "https://api.twitch.tv/helix/bits/cheermotes"
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Client-Id": self._client_id,
        }
        params = {}

        if broadcaster_id is not None:
            params = {"broadcaster_id": broadcaster_id}

        cheermotes = await http.send_get(url, headers, params)

        return [
            Cheermote(
                cheermote["prefix"],
                [
                    CheermoteTier(
                        tier["min_bits"],
                        tier["tier_id"],
                        tier["color"],
                        tier["images"],
                        tier["can_cheer"],
                        tier["show_in_bits_card"],
                    )
                    for tier in cheermote["tier"]
                ],
                cheermote["type"],
                cheermote["order"],
                cheermote["last_updated"],
                cheermote["is_charitable"],
            )
            for cheermote in cheermotes
        ]

    async def get_extension_transactions(
        self,
        extension_id: str,
        transaction_ids: list[str] | None = None,
        first: int = 20,
    ) -> list[ExtensionTransaction]:
        url = "https://api.twitch.tv/helix/extensions/transactions"
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Client-Id": self._client_id,
        }
        params = {}
        params["extension_id"] = extension_id

        if transaction_ids is not None and len(transaction_ids) > 0:
            params["id"] = transaction_ids

        transactions = await http.send_get_with_pagination(
            url, headers, params, first, 100
        )

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
