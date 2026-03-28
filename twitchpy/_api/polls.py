from datetime import datetime

from .._utils import date, http
from ..dataclasses import Channel, Poll, PollChoice, User

ENDPOINT_POLLS = "https://api.twitch.tv/helix/polls"


class PollsAPI:
    def __init__(self, access_token: str, client_id: str):
        self._access_token = access_token
        self._client_id = client_id

    async def get_polls(
        self,
        broadcaster_id: str,
        poll_ids: list[str] | None = None,
        first: int = 20,
    ) -> list[Poll]:
        url = ENDPOINT_POLLS
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Client-Id": self._client_id,
        }
        params = {}
        params["broadcaster_id"] = broadcaster_id

        if poll_ids is not None and len(poll_ids) > 0:
            params["id"] = poll_ids

        polls = await http.send_get_with_pagination(url, headers, params, first, 20)

        return [
            Poll(
                poll["id"],
                Channel(
                    User(
                        poll["broadcaster_id"],
                        poll["broadcaster_login"],
                        poll["broadcaster_name"],
                    )
                ),
                poll["title"],
                [
                    PollChoice(
                        choice["id"],
                        choice["title"],
                        choice["votes"],
                        choice["channel_points_votes"],
                    )
                    for choice in poll["choices"]
                ],
                poll["channel_points_voting_enabled"],
                poll["channel_points_per_vote"],
                poll["status"],
                poll["duration"],
                datetime.strptime(poll["started_at"], date.RFC3339_FORMAT),
                datetime.strptime(poll["ended_at"], date.RFC3339_FORMAT),
            )
            for poll in polls
        ]

    async def create_poll(
        self,
        broadcaster_id: str,
        title: str,
        choices: list[str],
        duration: int,
        channel_points_voting_enabled: bool = False,
        channel_points_per_vote: int = 0,
    ) -> Poll:
        url = ENDPOINT_POLLS
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Client-Id": self._client_id,
            "Content-Type": "application/json",
        }

        choices_dicts = [{"title": choice} for choice in choices]

        payload = {
            "broadcaster_id": broadcaster_id,
            "title": title,
            "choices": choices_dicts,
            "duration": duration,
            "channel_points_voting_enabled": channel_points_voting_enabled,
            "channel_points_per_vote": channel_points_per_vote,
        }

        poll = (await http.send_post_get_result(url, headers, payload))[0]

        return Poll(
            poll["id"],
            Channel(
                User(
                    poll["broadcaster_id"],
                    poll["broadcaster_login"],
                    poll["broadcaster_name"],
                )
            ),
            poll["title"],
            [
                PollChoice(
                    choice["id"],
                    choice["title"],
                    choice["votes"],
                    choice["channel_points_votes"],
                )
                for choice in poll["choices"]
            ],
            poll["channel_points_voting_enabled"],
            poll["channel_points_per_vote"],
            poll["status"],
            poll["duration"],
            datetime.strptime(poll["started_at"], date.RFC3339_FORMAT),
            datetime.strptime(poll["ended_at"], date.RFC3339_FORMAT),
        )

    async def end_poll(self, broadcaster_id: str, poll_id: str, status: str) -> Poll:
        url = ENDPOINT_POLLS
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Client-Id": self._client_id,
        }
        data = {"broadcaster_id": broadcaster_id, "id": poll_id, "status": status}

        poll = (await http.send_patch_get_result(url, headers, data))[0]

        return Poll(
            poll["id"],
            Channel(
                User(
                    poll["broadcaster_id"],
                    poll["broadcaster_login"],
                    poll["broadcaster_name"],
                )
            ),
            poll["title"],
            [
                PollChoice(
                    choice["id"],
                    choice["title"],
                    choice["votes"],
                    choice["channel_points_votes"],
                )
                for choice in poll["choices"]
            ],
            poll["channel_points_voting_enabled"],
            poll["channel_points_per_vote"],
            poll["status"],
            poll["duration"],
            datetime.strptime(poll["started_at"], date.RFC3339_FORMAT),
            datetime.strptime(poll["ended_at"], date.RFC3339_FORMAT),
        )
