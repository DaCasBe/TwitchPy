import json

import aiohttp

from . import errors
from ._api.ads import AdsAPI
from ._api.analytics import AnalyticsAPI
from ._api.bits import BitsAPI
from ._api.channel import ChannelsAPI
from ._api.channel_points import ChannelPointsAPI
from ._api.charity import CharityAPI
from ._api.chat import ChatAPI
from ._api.clips import ClipsAPI
from ._api.conduits import ConduitsAPI
from ._api.content_classification_labels import ContentClassificationLabelsAPI
from ._api.entitlements import EntitlementsAPI
from ._api.eventsub import EventSubAPI
from ._api.extensions import ExtensionsAPI
from ._api.games import GamesAPI
from ._api.goals import GoalsAPI
from ._api.guest_star import GuestStarAPI
from ._api.hype_train import HypeTrainAPI
from ._api.moderation import ModerationAPI
from ._api.polls import PollsAPI
from ._api.predictions import PredictionsAPI
from ._api.raids import RaidsAPI
from ._api.schedule import ScheduleAPI
from ._api.search import SearchAPI
from ._api.streams import StreamsAPI
from ._api.subscriptions import SubscriptionsAPI
from ._api.tags import TagsAPI
from ._api.teams import TeamsAPI
from ._api.users import UsersAPI
from ._api.videos import VideosAPI
from ._api.whispers import WhispersAPI
from .dataclasses import TokenInfo

_URL_OAUTH2_TOKEN = "https://id.twitch.tv/oauth2/token"
_URL_OAUTH2_VALIDATE = "https://id.twitch.tv/oauth2/validate"
_DEFAULT_TIMEOUT = 10


class Client:
    """
    Represents a client connection to the Twitch API
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        access_token: str,
        jwt_token: str | None = None,
    ):
        """
        Args:
            client_id (str): Client ID
            client_secret (str): Client secret
            access_token (str): Access token
            jwt_token (str, optional): JWT Token
        """

        self._client_id = client_id
        self._client_secret = client_secret
        self._access_token = access_token
        self._jwt_token = jwt_token

        self.ads = AdsAPI(self._access_token, self._client_id)
        self.analytics = AnalyticsAPI(self._access_token, self._client_id)
        self.bits = BitsAPI(self._access_token, self._client_id)
        self.channels = ChannelsAPI(self._access_token, self._client_id)
        self.channel_points = ChannelPointsAPI(self._access_token, self._client_id)
        self.charity = CharityAPI(self._access_token, self._client_id)
        self.chat = ChatAPI(self._access_token, self._client_id)
        self.clips = ClipsAPI(self._access_token, self._client_id)
        self.conduits = ConduitsAPI(self._access_token, self._client_id)
        self.content_classification_labels = ContentClassificationLabelsAPI(
            self._access_token, self._client_id
        )
        self.entitlements = EntitlementsAPI(self._access_token, self._client_id)
        self.extensions = ExtensionsAPI(
            self._client_id, self._access_token, self._jwt_token
        )
        self.eventsub = EventSubAPI(self._access_token, self._client_id)
        self.games = GamesAPI(self._access_token, self._client_id)
        self.goals = GoalsAPI(self._access_token, self._client_id)
        self.guest_star = GuestStarAPI(self._access_token, self._client_id)
        self.hype_train = HypeTrainAPI(self._access_token, self._client_id)
        self.moderation = ModerationAPI(self._access_token, self._client_id)
        self.polls = PollsAPI(self._access_token, self._client_id)
        self.predictions = PredictionsAPI(self._access_token, self._client_id)
        self.raids = RaidsAPI(self._access_token, self._client_id)
        self.schedule = ScheduleAPI(self._access_token, self._client_id)
        self.search = SearchAPI(self._access_token, self._client_id)
        self.streams = StreamsAPI(self._access_token, self._client_id)
        self.subscriptions = SubscriptionsAPI(self._access_token, self._client_id)
        self.tags = TagsAPI(self._access_token, self._client_id)
        self.teams = TeamsAPI(self._access_token, self._client_id)
        self.users = UsersAPI(self._access_token, self._client_id)
        self.videos = VideosAPI(self._access_token, self._client_id)
        self.whispers = WhispersAPI(self._access_token, self._client_id)

    async def validate_token(self) -> TokenInfo:
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=_DEFAULT_TIMEOUT)
        ) as session:
            url = _URL_OAUTH2_VALIDATE
            headers = {"Authorization": f"OAuth {self._access_token}"}

            async with session.get(url, headers=headers) as response:
                if not response.ok:
                    raise errors.ClientError("Invalid client authorization")

                token_info = await response.json()
                return TokenInfo(
                    token_info["client_id"],
                    token_info["login"],
                    token_info["scopes"],
                    token_info["user_id"],
                    token_info["expires_in"],
                )

    async def refresh_user_tokens(self, refresh_user_token: str) -> None:
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=_DEFAULT_TIMEOUT)
        ) as session:
            url = _URL_OAUTH2_TOKEN
            payload = {
                "grant_type": "refresh_token",
                "refresh_token": refresh_user_token,
                "client_id": self._client_id,
                "client_secret": self._client_secret,
            }

            async with session.post(url, json=payload) as response:
                if not response.ok:
                    raise errors.UserTokenError("Error obtaining user token")

                tokens = await response.json()
                self._save_tokens(tokens["access_token"], tokens["refresh_token"])

    def _save_tokens(self, access_token: str, refresh_token: str) -> None:
        with open("tokens.json", "wt") as tokens_file:
            json.dump(
                {"access_token": access_token, "refresh_token": refresh_token},
                tokens_file,
            )
