import json

import requests

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

        self.client_id = client_id
        self.client_secret = client_secret
        self.__access_token = access_token
        self.__jwt_token = jwt_token

        self.ads = AdsAPI(self.__access_token, self.client_id)
        self.analytics = AnalyticsAPI(self.__access_token, self.client_id)
        self.bits = BitsAPI(self.__access_token, self.client_id)
        self.channels = ChannelsAPI(self.__access_token, self.client_id)
        self.channel_points = ChannelPointsAPI(self.__access_token, self.client_id)
        self.charity = CharityAPI(self.__access_token, self.client_id)
        self.chat = ChatAPI(self.__access_token, self.client_id)
        self.clips = ClipsAPI(self.__access_token, self.client_id)
        self.conduits = ConduitsAPI(self.__access_token, self.client_id)
        self.content_classification_labels = ContentClassificationLabelsAPI(
            self.__access_token, self.client_id
        )
        self.entitlements = EntitlementsAPI(self.__access_token, self.client_id)
        self.extensions = ExtensionsAPI(
            self.client_id, self.__access_token, self.__jwt_token
        )
        self.eventsub = EventSubAPI(self.__access_token, self.client_id)
        self.games = GamesAPI(self.__access_token, self.client_id)
        self.goals = GoalsAPI(self.__access_token, self.client_id)
        self.guest_star = GuestStarAPI(self.__access_token, self.client_id)
        self.hype_train = HypeTrainAPI(self.__access_token, self.client_id)
        self.moderation = ModerationAPI(self.__access_token, self.client_id)
        self.polls = PollsAPI(self.__access_token, self.client_id)
        self.predictions = PredictionsAPI(self.__access_token, self.client_id)
        self.raids = RaidsAPI(self.__access_token, self.client_id)
        self.schedule = ScheduleAPI(self.__access_token, self.client_id)
        self.search = SearchAPI(self.__access_token, self.client_id)
        self.streams = StreamsAPI(self.__access_token, self.client_id)
        self.subscriptions = SubscriptionsAPI(self.__access_token, self.client_id)
        self.tags = TagsAPI(self.__access_token, self.client_id)
        self.teams = TeamsAPI(self.__access_token, self.client_id)
        self.users = UsersAPI(self.__access_token, self.client_id)
        self.videos = VideosAPI(self.__access_token, self.client_id)
        self.whispers = WhispersAPI(self.__access_token, self.client_id)

    def validate_token(self) -> TokenInfo:
        url = _URL_OAUTH2_VALIDATE
        response = requests.get(
            url,
            headers={"Authorization": f"OAuth {self.__access_token}"},
            timeout=_DEFAULT_TIMEOUT,
        )

        if response.ok:
            response = response.json()
            return TokenInfo(
                response["client_id"],
                response["login"],
                response["scopes"],
                response["user_id"],
                response["expires_in"],
            )

        else:
            raise errors.ClientError("Invalid client authorization")

    def refresh_user_tokens(self, refresh_user_token: str) -> None:
        url = _URL_OAUTH2_TOKEN
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_user_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        response = requests.post(url, json=payload, timeout=_DEFAULT_TIMEOUT)

        if response.ok:
            response = response.json()
            self.__save_tokens(response["access_token"], response["refresh_token"])

        else:
            raise errors.UserTokenError("Error obtaining user token")

    def __save_tokens(self, access_token: str, refresh_token: str) -> None:
        with open("tokens.json", "wt") as tokens_file:
            json.dump(
                {"access_token": access_token, "refresh_token": refresh_token},
                tokens_file,
            )
