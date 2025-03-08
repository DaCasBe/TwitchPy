import logging
import os
from datetime import datetime

import requests

from . import errors
from ._api import (
    ads,
    analytics,
    bits,
    channels,
    charity_campaigns,
    chats,
    clips,
    content_classification_labels,
    drops,
    eventsubs,
    extensions,
    games,
    goals,
    guest_stars,
    hype_trains,
    moderation,
    polls,
    predictions,
    raids,
    rewards,
    schedules,
    searchs,
    streams,
    subscriptions,
    tags,
    teams,
    users,
    videos,
    whispers,
)
from .dataclasses import (
    AdSchedule,
    AutoModSettings,
    Badge,
    BannedUser,
    BitsLeaderboardLeader,
    BlockedTerm,
    Channel,
    CharityCampaign,
    CharityCampaignDonation,
    ChatSettings,
    ChatterWarning,
    Cheermote,
    Clip,
    Commercial,
    Conduit,
    ConduitShard,
    ContentClassificationLabel,
    CreatorGoal,
    DropEntitlement,
    Emote,
    EventSubSubscription,
    Extension,
    ExtensionAnalyticsReport,
    ExtensionConfigurationSegment,
    ExtensionSecret,
    ExtensionTransaction,
    Game,
    GameAnalyticsReport,
    GuestStarInvite,
    GuestStarSession,
    GuestStarSettings,
    HypeTrainEvent,
    Poll,
    Prediction,
    Product,
    Redemption,
    Reward,
    ShieldModeStatus,
    Stream,
    StreamMarker,
    StreamSchedule,
    Subscription,
    Tag,
    Team,
    TokenInfo,
    Transport,
    UnbanRequest,
    User,
    Video,
)

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
        redirect_uri: str,
        tokens_path: str,
        authorization_code: str | None = None,
        jwt_token: str | None = None,
    ):
        """
        Args:
            client_id (str): Client ID
            client_secret (str): Client secret
            redirect_uri (str): Redirect URI
            tokens_path (str): Path of tokens file (file included)
            authorization_code (str, optional): Authorization code for getting an user token
            jwt_token (str, optional): JWT Token
        """

        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.tokens_path = tokens_path
        self.__app_token = self.__get_app_token()

        if authorization_code is not None:
            self.__user_token = self.__get_user_token(authorization_code)

        else:
            self.__user_token = ""

        self.__jwt_token = jwt_token if jwt_token is not None else ""

    def __get_app_token(self) -> str:
        url = _URL_OAUTH2_TOKEN
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials",
        }

        response = requests.post(url, json=payload, timeout=_DEFAULT_TIMEOUT)

        if response.ok:
            return response.json()["access_token"]

        else:
            raise errors.AppTokenError("Error obtaining app token")

    def __is_last_code_used(self, authorization_code: str) -> bool:
        with open(self.tokens_path, encoding="UTF-8") as tokens_file:
            tokens = tokens_file.readlines()

        for token in tokens:
            token = token.replace(" ", "").replace("\n", "")
            token = token.split("=")

            if token[0] == "CODE" and token[1] == authorization_code:
                return True

        return False

    def __read_user_tokens_from_file(self, file: str) -> tuple[str, str]:
        try:
            secret_file = open(file, "rt", encoding="UTF-8")
            data = secret_file.readlines()
            secret_file.close()

        except Exception as error:
            logging.exception("Error reading tokens")
            raise error

        user_token = ""
        refresh_user_token = ""

        for token in data:
            secret = token.split("=")

            if "USER_TOKEN" == secret[0]:
                user_token = secret[1].replace("\n", "")

            if "REFRESH_USER_TOKEN" == secret[0]:
                refresh_user_token = secret[1].replace("\n", "")

        return user_token, refresh_user_token

    def __save_user_tokens_in_file(
        self,
        file: str,
        user_token: str,
        user_refresh_token: str,
        authorization_code: str,
    ) -> None:
        data = f"USER_TOKEN={user_token}\nREFRESH_USER_TOKEN={user_refresh_token}\nCODE={authorization_code}"

        secret_file = open(file, "wt", encoding="UTF-8")
        secret_file.write(data)
        secret_file.close()

    def __generate_user_tokens(
        self, authorization_code: str, file: str
    ) -> tuple[str, str]:
        url = _URL_OAUTH2_TOKEN
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": authorization_code,
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_uri,
        }

        response = requests.post(url, payload, timeout=_DEFAULT_TIMEOUT)

        if response.ok:
            response = response.json()
            self.__save_user_tokens_in_file(
                file,
                response["access_token"],
                response["refresh_token"],
                authorization_code,
            )

            return response["access_token"], response["refresh_token"]

        else:
            raise errors.ClientError(response.json()["message"])

    def __refresh_user_tokens(self, refresh_user_token: str) -> tuple[str, str]:
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
            return response["access_token"], response["refresh_token"]

        else:
            raise errors.UserTokenError("Error obtaining user token")

    def __get_user_token(self, authorization_code: str) -> str:
        if not os.path.isfile(self.tokens_path):
            file = open(self.tokens_path, "w", encoding="UTF-8")
            file.close()

        if self.__is_last_code_used(authorization_code):
            user_token, refresh_user_token = self.__read_user_tokens_from_file(
                self.tokens_path
            )
            user_token, refresh_user_token = self.__refresh_user_tokens(
                refresh_user_token
            )
            self.__save_user_tokens_in_file(
                self.tokens_path, user_token, refresh_user_token, authorization_code
            )

        else:
            user_token, refresh_user_token = self.__generate_user_tokens(
                authorization_code, self.tokens_path
            )

        return user_token

    def validate_token(self) -> TokenInfo:
        url = _URL_OAUTH2_VALIDATE
        response = requests.get(url, headers={"Authorization": f"OAuth {self.__user_token}"}, timeout=_DEFAULT_TIMEOUT)

        if response.ok:
            response = response.json()
            return TokenInfo(
                    response["client_id"],
                    response["login"],
                    response["scopes"],
                    response["user_id"],
                    response["expires_in"]
                    )

        else:
            raise errors.ClientError("Invalid client authorization")


    def start_commercial(self, broadcaster_id: int, length: int) -> Commercial:
        """
        Starts a commercial on a specified channel

        Args:
            broadcaster_id (int): ID of the channel requesting a commercial
            length (int): Desired length of the commercial in seconds
                Valid options are 30, 60, 90, 120, 150 and 180

        Raises:
            errors.ClientError

        Returns:
            Commercial
        """

        return ads.start_commercial(
            self.__user_token, self.client_id, broadcaster_id, length
        )

    def get_ad_schedule(self, broadcaster_id: str) -> AdSchedule:
        """
        Returns ad schedule related information, including snooze, when the last ad was run, when the next ad is scheduled, and if the channel is currently in pre-roll free time

        Args:
            broadcaster_id (str): Provided broadcaster_id must match the user_id in the auth token

        Raises:
            errors.ClientError

        Returns:
            AdSchedule
        """

        return ads.get_ad_schedule(self.__user_token, self.client_id, broadcaster_id)

    def snooze_next_ad(self, broadcaster_id: str) -> AdSchedule:
        """
        If available, pushes back the timestamp of the upcoming automatic mid-roll ad by 5 minutes

        Args:
            broadcaster_id (str): Provided broadcaster_id must match the user_id in the auth token

        Raises:
            errors.ClientError

        Returns:
            AdSchedule
        """

        return ads.snooze_next_ad(self.__user_token, self.client_id, broadcaster_id)

    def get_extension_analytics(
        self,
        extension_id: str | None = None,
        report_type: str | None = None,
        started_at: datetime | None = None,
        ended_at: datetime | None = None,
        first: int = 20,
    ) -> list[ExtensionAnalyticsReport]:
        """
        Gets a URL that Extension developers can use to download analytics reports for their Extensions
        The URL is valid for 5 minutes

        Args:
            extension_id (str | None): Client ID value assigned to the extension when it is created
            report_type (str | None): Type of analytics report that is returned
                Valid values: "overview_v2"
            started_at (datetime | None): Starting date/time for returned reports, in RFC3339 format with the hours, minutes, and seconds zeroed out and the UTC timezone: YYYY-MM-DDT00:00:00Z
                This must be on or after January 31, 2018
                If this is provided, ended_at also must be specified
            ended_at (datetime | None): Ending date/time for returned reports, in RFC3339 format with the hours, minutes, and seconds zeroed out and the UTC timezone: YYYY-MM-DDT00:00:00Z
                If this is provided, started_at also must be specified
            first (int): Maximum number of objects to return
                Default: 20

        Raises:
            errors.ClientError

        Returns:
            list[ExtensionAnalyticsReport]
        """

        return analytics.get_extension_analytics(
            self.__user_token,
            self.client_id,
            extension_id,
            report_type,
            started_at,
            ended_at,
            first,
        )

    def get_game_analytics(
        self,
        game_id: str | None = None,
        report_type: str | None = None,
        started_at: datetime | None = None,
        ended_at: datetime | None = None,
        first: int = 20,
    ) -> list[GameAnalyticsReport]:
        """
        Gets a URL that game developers can use to download analytics reports for their games
        The URL is valid for 5 minutes

        Args:
            game_id (str | None): Game ID
            report_type (str | None): Type of analytics report that is returned
                Valid values: "overview_v2"
            started_at (datetime | None): Starting date/time for returned reports, in RFC3339 format with the hours, minutes, and seconds zeroed out and the UTC timezone: YYYY-MM-DDT00:00:00Z
                If this is provided, ended_at also must be specified
            ended_at (datetime | None): Ending date/time for returned reports, in RFC3339 format with the hours, minutes, and seconds zeroed out and the UTC timezone: YYYY-MM-DDT00:00:00Z
                If this is provided, started_at also must be specified
            first (int): Maximum number of objects to return
                Default: 20

        Raises:
            errors.ClientError

        Returns:
            list[GameAnalyticsReport]
        """

        return analytics.get_game_analytics(
            self.__user_token,
            self.client_id,
            game_id,
            report_type,
            started_at,
            ended_at,
            first,
        )

    def get_bits_leaderboard(
        self,
        count: int = 10,
        period: str = "all",
        started_at: datetime | None = None,
        user_id: str | None = None,
    ) -> list[BitsLeaderboardLeader]:
        """
        Gets a ranked list of Bits leaderboard information for a broadcaster

        Args:
            count (int): Number of results to be returned
                Maximum: 100
                Default: 10
            period (str): Time period over which data is aggregated (PST time zone)
                This parameter interacts with started_at
                Default: "all"
                Valid values: "day", "week", "month", "year", "all"
            started_at (datetime | None): Timestamp for the period over which the returned data is aggregated
                Must be in RFC 3339 format
                This value is ignored if period is "all"
            user_id (str | None): ID of the user whose results are returned
                As long as count is greater than 1, the returned data includes additional users, with Bits amounts above and below the user specified

        Raises:
            errors.ClientError

        Returns:
            list[BitsLeaderboardLeader]
        """

        return bits.get_bits_leaderboard(
            self.__user_token, self.client_id, count, period, started_at, user_id
        )

    def get_cheermotes(self, broadcaster_id: str | None = None) -> list[Cheermote]:
        """
        Retrieves the list of available Cheermotes
        Cheermotes returned are available throughout Twitch, in all Bits-enabled channels

        Args:
            broadcaster_id (str | None): ID for the broadcaster who might own specialized Cheermotes

        Raises:
            errors.ClientError

        Returns:
            list[Cheermote]
        """

        return bits.get_cheermotes(
            self.__user_token if self.__user_token != "" else self.__app_token,
            self.client_id,
            broadcaster_id,
        )

    def get_extension_transactions(
        self,
        extension_id: str,
        transaction_ids: list[str] | None = None,
        first: int = 20,
    ) -> list[ExtensionTransaction]:
        """
        Allows extension back-end servers to fetch a list of transactions that have occurred for their extension across all of Twitch
        A transaction is a record of a user exchanging Bits for an in-Extension digital good

        Args:
            extension_id (str): ID of the extension to list transactions for
            transaction_ids (list[str] | None): Transaction IDs to look up
                Maximum: 100
            first (int): Maximum number of objects to return
                Default: 20

        Raises:
            errors.ClientError

        Returns:
            list[ExtensionTransaction]
        """

        return extensions.get_extension_transactions(
            self.__app_token, self.client_id, extension_id, transaction_ids, first
        )

    def get_channel_information(self, broadcaster_id: list[str]) -> list[Channel]:
        """
        Gets one or more channels

        Args:
            broadcaster_id (list[str]): The ID of the broadcaster whose channel you want to get
                Maximum: 100

        Raises:
            errors.ClientError

        Returns:
            list[Channel]
        """

        return channels.get_channel_information(
            self.__user_token if self.__user_token != "" else self.__app_token,
            self.client_id,
            broadcaster_id,
        )

    def modify_channel_information(
        self,
        broadcaster_id: str,
        game_id: str | None = None,
        broadcaster_language: str | None = None,
        title: str | None = None,
        delay: int | None = None,
        channel_tags: list[str] | None = None,
        cc_labels: list[ContentClassificationLabel] | None = None,
        is_branded_content: bool | None = None,
    ) -> None:
        """
        Updates a channel’s properties

        Args:
            broadcaster_id (str): The ID of the broadcaster whose channel you want to update
                ID must match the user ID in the user access token
            game_id (str | None): The ID of the game that the user plays
            broadcaster_language (str | None): The user’s preferred language
                Set the value to an ISO 639-1 two-letter language code
                Set to “other” if the user’s preferred language is not a Twitch supported language
            title (str | None): The title of the user’s stream
            delay (int | None): The number of seconds you want your broadcast buffered before streaming it live
                Only users with Partner status may set this field
                Maximum: 900 seconds
            channel_tags (list[str] | None): A list of channel-defined tags to apply to the channel
                Maximum: 10
            cc_labels (list[ContentClassificationLabel] | None): List of labels that should be set as the Channel’s CCLs
            is_branded_content (bool | None): Boolean flag indicating if the channel has branded content

        Raises:
            errors.ClientError
        """

        channels.modify_channel_information(
            self.__user_token,
            self.client_id,
            broadcaster_id,
            game_id,
            broadcaster_language,
            title,
            delay,
            channel_tags,
            cc_labels,
            is_branded_content,
        )

    def get_channel_editors(self, broadcaster_id: str) -> list[User]:
        """
        Gets a list of users who have editor permissions for a specific channel

        Args:
            broadcaster_id (str): Broadcaster’s user ID associated with the channel

        Raises:
            errors.ClientError

        Returns:
            list[User]
        """

        return channels.get_channel_editors(
            self.__user_token, self.client_id, broadcaster_id
        )

    def get_followed_channels(
        self, user_id: str, broadcaster_id: str | None = None, first: int = 20
    ) -> list[tuple[Channel, datetime]]:
        """
        Gets a list of broadcasters that the specified user follows

        Args:
            user_id (str): A user’s ID
                Returns the list of broadcasters that this user follows
                This ID must match the user ID in the user OAuth token
            broadcaster_id (str | None): A broadcaster’s ID
                Use this parameter to see whether the user follows this broadcaster
            first (int): The maximum number of items to return
                Default: 20
                Minimum: 1

        Raises:
            errors.ClientError

        Returns:
            list[tuple[Channel, datetime]]
        """

        return channels.get_followed_channels(
            self.__user_token, self.client_id, user_id, broadcaster_id, first
        )

    def get_channel_followers(
        self, broadcaster_id: str, user_id: str | None = None, first: int = 20
    ) -> list[tuple[Channel, datetime]]:
        """
        The function `get_channel_followers` retrieves a list of channels that are following a specific
        broadcaster on Twitch.

        Args:
            broadcaster_id (str): The broadcaster’s ID
                Returns the list of users that follow this broadcaster
            user_id (str | None): A user’s ID
                Use this parameter to see whether the user follows this broadcaster
            first (int): The maximum number of items to return
                Default: 20
                Minimum: 1

        Raises:
            errors.ClientError

        Returns:
            list[tuple[Channel, datetime]]
        """

        return channels.get_channel_followers(
            self.__user_token, self.client_id, broadcaster_id, user_id, first
        )

    def create_custom_reward(
        self,
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
        """
        Creates a Custom Reward on a channel

        Args:
            broadcaster_id (str): ID of the channel creating a reward
            title (str): The title of the reward
            cost (int): The cost of the reward
            prompt (str | None): The prompt for the viewer when they are redeeming the reward
            is_enabled (bool): Is the reward currently enabled, if false the reward won’t show up to viewers
                Default: true
            background_color (str | None): Custom background color for the reward
                Format: Hex with # prefix
            is_user_input_required (bool): Does the user need to enter information when redeeming the reward
                Default: false
            is_max_per_stream_enabled (bool): Whether a maximum per stream is enabled
                Default: false
            max_per_stream (int | None): The maximum number per stream if enabled
                Required when any value of is_max_per_stream_enabled is included
            is_max_per_user_per_stream_enabled (bool): Whether a maximum per user per stream is enabled
                Default: false
            max_per_user_per_stream (int | None): The maximum number per user per stream if enabled
                Required when any value of is_max_per_user_per_stream_enabled is included
            is_global_cooldown_enabled (bool): Whether a cooldown is enabled
                Default: false
            global_cooldown_seconds (int | None): The cooldown in seconds if enabled
                Required when any value of is_global_cooldown_enabled is included
            should_redemptions_skip_request_queue (bool): Should redemptions be set to FULFILLED status immediately when redeemed and skip the request queue instead of the normal UNFULFILLED status
                Default: false

        Raises:
            errors.ClientError

        Returns:
            Reward
        """

        return rewards.create_custom_reward(
            self.__user_token,
            self.client_id,
            broadcaster_id,
            title,
            cost,
            prompt,
            is_enabled,
            background_color,
            is_user_input_required,
            is_max_per_stream_enabled,
            max_per_stream,
            is_max_per_user_per_stream_enabled,
            max_per_user_per_stream,
            is_global_cooldown_enabled,
            global_cooldown_seconds,
            should_redemptions_skip_request_queue,
        )

    def delete_custom_reward(self, broadcaster_id: str, reward_id: str) -> None:
        """
        Deletes a Custom Reward on a channel
        The Custom Reward specified by id must have been created by the client_id attached to the OAuth token in order to be deleted
        Any UNFULFILLED Custom Reward Redemptions of the deleted Custom Reward will be updated to the FULFILLED status

        Args:
            broadcaster_id (str): Provided broadcaster_id must match the user_id in the user OAuth token
            reward_id (str): ID of the Custom Reward to delete
                Must match a Custom Reward on broadcaster_id’s channel

        Raises:
            errors.ClientError
        """

        rewards.delete_custom_reward(
            self.__user_token, self.client_id, broadcaster_id, reward_id
        )

    def get_custom_reward(
        self,
        broadcaster_id: str,
        reward_ids: list[str] | None = None,
        only_manageable_rewards: bool = False,
    ) -> list[Reward]:
        """
        Returns a list of Custom Reward objects for the Custom Rewards on a channel

        Args:
            broadcaster_id (str): Provided broadcaster_id must match the user_id in the user OAuth token
            reward_ids (list[str] | None): This parameter filters the results and only returns reward objects for the Custom Rewards with matching ID
                Maximum: 50
            only_manageable_rewards (bool): When set to true, only returns custom rewards that the calling broadcaster can manage
                Default: false

        Raises:
            errors.ClientError

        Returns:
            list[Reward]
        """

        return rewards.get_custom_reward(
            self.__user_token,
            self.client_id,
            broadcaster_id,
            reward_ids,
            only_manageable_rewards,
        )

    def get_custom_reward_redemption(
        self,
        broadcaster_id: str,
        reward_id: str,
        redemption_ids: list[str] | None = None,
        status: str | None = None,
        sort: str = "OLDEST",
        first: int = 20,
    ) -> list[Redemption]:
        """
        Returns Custom Reward Redemption objects for a Custom Reward on a channel that was created by the same client_id
        Developers only have access to get and update redemptions for the rewards created programmatically by the same client_id

        Args:
            broadcaster_id (str): Provided broadcaster_id must match the user_id in the user OAuth token
            reward_id (str): When ID is not provided, this parameter returns Custom Reward Redemption objects for redemptions of the Custom Reward with ID reward_id
            redemption_ids (list[str] | None): When id is not provided, this param filters the results and only returns Custom Reward Redemption objects for the redemptions with matching ID
                Maximum: 50
            status (str | None): This param filters the Custom Reward Redemption objects for redemptions with the matching status
                Can be one of UNFULFILLED, FULFILLED or CANCELED
            sort (str): Sort order of redemptions returned when getting the Custom Reward Redemption objects for a reward
                One of: OLDEST, NEWEST
                Default: OLDEST
            first (int): Number of results to be returned when getting the Custom Reward Redemption objects for a reward
                Default: 20

        Raises:
            errors.ClientError

        Returns:
            list[Redemption]
        """

        return rewards.get_custom_reward_redemption(
            self.__user_token,
            self.client_id,
            broadcaster_id,
            reward_id,
            redemption_ids,
            status,
            sort,
            first,
        )

    def update_custom_reward(
        self,
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
        """
        Updates a Custom Reward created on a channel
        The Custom Reward specified by id must have been created by the client_id attached to the user OAuth token

        Args:
            broadcaster_id (str): Provided broadcaster_id must match the user_id in the user OAuth token
            reward_id (str): ID of the Custom Reward to update
                Must match a Custom Reward on the channel of the broadcaster_id
            title (str | None): The title of the reward
            prompt (str | None): The prompt for the viewer when they are redeeming the reward
            cost (int | None): The cost of the reward
            background_color (str | None): Custom background color for the reward as a hexadecimal value
            is_enabled (bool | None): Is the reward currently enabled, if false the reward won’t show up to viewers
            is_user_input_required (bool | None): Does the user need to enter information when redeeming the reward
            is_max_per_stream_enabled (bool | None): Whether a maximum per stream is enabled
                Required when any value of max_per_stream is included
            max_per_stream (int | None): The maximum number per stream if enabled
                Required when any value of is_max_per_stream_enabled is included
            is_max_per_user_per_stream_enabled (bool | None): Whether a maximum per user per stream is enabled
                Required when any value of max_per_user_per_stream is included
            max_per_user_per_stream (int | None): The maximum number per user per stream if enabled
                Required when any value of is_max_per_user_per_stream_enabled is included
            is_global_cooldown_enabled (bool | None): Whether a cooldown is enabled
                Required when any value of global_cooldown_seconds is included
            global_cooldown_seconds (int | None): The cooldown in seconds if enabled
                Required when any value of is_global_cooldown_enabled is included
            is_paused (bool | None): Is the reward currently paused, if true viewers cannot redeem
            should_redemptions_skip_request_queue (bool | None): Should redemptions be set to FULFILLED status immediately when redeemed and skip the request queue instead of the normal UNFULFILLED status

        Raises:
            errors.ClientError

        Returns:
            Reward
        """

        return rewards.update_custom_reward(
            self.__user_token,
            self.client_id,
            broadcaster_id,
            reward_id,
            title,
            prompt,
            cost,
            background_color,
            is_enabled,
            is_user_input_required,
            is_max_per_stream_enabled,
            max_per_stream,
            is_max_per_user_per_stream_enabled,
            max_per_user_per_stream,
            is_global_cooldown_enabled,
            global_cooldown_seconds,
            is_paused,
            should_redemptions_skip_request_queue,
        )

    def update_redemption_status(
        self,
        redemption_id: list[str],
        broadcaster_id: str,
        reward_id: str,
        status: str | None = None,
    ) -> list[Redemption]:
        """
        Updates the status of Custom Reward Redemption objects on a channel that are in the UNFULFILLED status
        The Custom Reward Redemption specified by id must be for a Custom Reward created by the client_id attached to the user OAuth token

        Args:
            redemption_id (list[str]): ID of the Custom Reward Redemption to update
                Must match a Custom Reward Redemption on broadcaster_id’s channel
                Maximum: 50
            broadcaster_id (str): Provided broadcaster_id must match the user_id in the user OAuth token
            reward_id (str): ID of the Custom Reward the redemptions to be updated are for
            status (str | None): The new status to set redemptions to
                Can be either FULFILLED or CANCELED
                Updating to CANCELED will refund the user their Channel Points

        Raises:
            errors.ClientError

        Returns:
            list[Redemption]
        """

        return rewards.update_redemption_status(
            self.__user_token,
            self.client_id,
            redemption_id,
            broadcaster_id,
            reward_id,
            status,
        )

    def get_charity_campaign(self, broadcaster_id: str) -> CharityCampaign:
        """
        Gets information about the charity campaign that a broadcaster is running

        Args:
            broadcaster_id (str): The ID of the broadcaster that’s currently running a charity campaign
                This ID must match the user ID in the access token

        Raises:
            errors.ClientError

        Returns:
            CharityCampaign
        """

        return charity_campaigns.get_charity_campaign(
            self.__user_token, self.client_id, broadcaster_id
        )

    def get_charity_campaign_donations(
        self, broadcaster_id: str, first: int = 20
    ) -> list[CharityCampaignDonation]:
        """
        Gets the list of donations that users have made to the broadcaster’s active charity campaign

        Args:
            broadcaster_id (str): The ID of the broadcaster that’s currently running a charity campaign
                This ID must match the user ID in the access token
            first (int): The maximum number of items to return
                Default: 20
                Minimum: 1

        Raises:
            errors.ClientError

        Returns:
            list[CharityCampaignDonation]
        """

        return charity_campaigns.get_charity_campaign_donations(
            self.__user_token, self.client_id, broadcaster_id, first
        )

    def get_chatters(
        self, broadcaster_id: str, moderator_id: str, first: int = 100
    ) -> list[User]:
        """
        Gets the list of users that are connected to the broadcaster’s chat session

        Args:
            broadcaster_id (str): The ID of the broadcaster whose list of chatters you want to get
            moderator_id (str): The ID of the broadcaster or one of the broadcaster’s moderators
                This ID must match the user ID in the user access token
            first (int): The maximum number of items to return
                Default: 100
                Minimum: 1

        Raises:
            errors.ClientError

        Returns:
            list[User]
        """

        return chats.get_chatters(
            self.__user_token, self.client_id, broadcaster_id, moderator_id, first
        )

    def get_channel_emotes(self, broadcaster_id: str) -> list[Emote]:
        """
        Gets all custom emotes for a specific Twitch channel including subscriber emotes, Bits tier emotes, and follower emotes
        Custom channel emotes are custom emoticons that viewers may use in Twitch chat once they are subscribed to, cheered in, or followed the channel that owns the emotes

        Args:
            broadcaster_id (str): The broadcaster whose emotes are being requested

        Raises:
            errors.ClientError

        Returns:
            list[Emote]
        """

        return chats.get_channel_emotes(
            self.__user_token if self.__user_token != "" else self.__app_token,
            self.client_id,
            broadcaster_id,
        )

    def get_global_emotes(self) -> list[Emote]:
        """
        Gets all global emotes
        Global emotes are Twitch-specific emoticons that every user can use in Twitch chat

        Raises:
            errors.ClientError

        Returns:
            list[Emote]
        """

        return chats.get_global_emotes(self.__app_token, self.client_id)

    def get_emote_sets(self, emote_set_id: list[str]) -> list[Emote]:
        """
        Gets all Twitch emotes for one or more specific emote sets

        Args:
            emote_set_id (list[str]): ID(s) of the emote set
                Maximum: 25

        Raises:
            errors.ClientError

        Returns:
            list[Emote]
        """

        return chats.get_emote_sets(self.__app_token, self.client_id, emote_set_id)

    def get_channel_chat_badges(self, broadcaster_id: str) -> list[Badge]:
        """
        Gets a list of custom chat badges that can be used in chat for the specified channel
        This includes subscriber badges and Bit badges

        Args:
            broadcaster_id (str): The broadcaster whose chat badges are being requested
                Provided broadcaster_id must match the user_id in the user OAuth token

        Raises:
            errors.ClientError

        Returns:
            list[Badge]
        """

        return chats.get_channel_chat_badges(
            self.__app_token, self.client_id, broadcaster_id
        )

    def get_global_chat_badges(self) -> list[Badge]:
        """
        Gets a list of chat badges that can be used in chat for any channel

        Raises:
            errors.ClientError

        Returns:
            list[Badge]
        """

        return chats.get_global_chat_badges(self.__app_token, self.client_id)

    def get_chat_settings(
        self, broadcaster_id: str, moderator_id: str | None = None
    ) -> ChatSettings:
        """
        Gets the broadcaster’s chat settings

        Args:
            broadcaster_id (str): The ID of the broadcaster whose chat settings you want to get
            moderator_id (str | None): Required only to access the non_moderator_chat_delay or non_moderator_chat_delay_duration settings
                The ID of a user that has permission to moderate the broadcaster’s chat room
                This ID must match the user ID associated with the user OAuth token
                If the broadcaster wants to get their own settings (instead of having the moderator do it), set this parameter to the broadcaster’s ID, too

        Raises:
            errors.ClientError

        Returns:
            ChatSettings
        """

        return chats.get_chat_settings(
            self.__user_token, self.client_id, broadcaster_id, moderator_id
        )

    def get_user_emotes(
        self, user_id: str, broadcaster_id: str | None = None
    ) -> list[Emote]:
        """
        Retrieves emotes available to the user across all channels

        Args:
            user_id (str): The ID of the user
                This ID must match the user ID in the user access token
            broadcaster_id (str | None): The User ID of a broadcaster you wish to get follower emotes of
                Using this query parameter will guarantee inclusion of the broadcaster’s follower emotes in the response body

        Raises:
            errors.ClientError

        Returns:
            list[Emote]
        """

        return chats.get_user_emotes(
            self.__user_token, self.client_id, user_id, broadcaster_id
        )

    def update_chat_settings(
        self,
        broadcaster_id: str,
        moderator_id: str,
        emote_mode: bool | None = None,
        follower_mode: bool | None = None,
        follower_mode_duration: int | None = None,
        non_moderator_chat_delay: bool | None = None,
        non_moderator_chat_delay_duration: int | None = None,
        slow_mode: bool | None = None,
        slow_mode_wait_time: int | None = None,
        subscriber_mode: bool | None = None,
        unique_chat_mode: bool | None = None,
    ) -> ChatSettings:
        """
        Updates the broadcaster’s chat settings

        Args:
            broadcaster_id (str): The ID of the broadcaster whose chat settings you want to update
                This ID must match the user ID associated with the user OAuth token
            moderator_id (str): The ID of a user that has permission to moderate the broadcaster’s chat room
                This ID must match the user ID associated with the user OAuth token
                If the broadcaster wants to update their own settings (instead of having the moderator do it), set this parameter to the broadcaster’s ID, too
            emote_mode (bool | None): A Boolean value that determines whether chat messages must contain only emotes
                Set to true, if only messages that are 100% emotes are allowed; otherwise, false
                Default is false
            follower_mode (bool | None): A Boolean value that determines whether the broadcaster restricts the chat room to followers only, based on how long they’ve followed
                Set to true, if the broadcaster restricts the chat room to followers only; otherwise, false
                Default is false
            follower_mode_duration (int | None): The length of time, in minutes, that the followers must have followed the broadcaster to participate in the chat room
                You may specify a value in the range: 0 (no restriction) through 129600 (3 months)
                The default is 0
            non_moderator_chat_delay (bool | None): A Boolean value that determines whether the broadcaster adds a short delay before chat messages appear in the chat room
                This gives chat moderators and bots a chance to remove them before viewers can see the message
                Set to true, if the broadcaster applies a delay; otherwise, false
                Default is false
            non_moderator_chat_delay_duration (int | None): The amount of time, in seconds, that messages are delayed from appearing in chat
                Possible values are: 2, 4, 6
            slow_mode (bool | None): A Boolean value that determines whether the broadcaster limits how often users in the chat room are allowed to send messages
                Set to true, if the broadcaster applies a wait period messages; otherwise, false
                Default is false
            slow_mode_wait_time (int | None): The amount of time, in seconds, that users need to wait between sending messages
                You may specify a value in the range: 3 (3 second delay) through 120 (2 minute delay)
                The default is 30 seconds
            subscriber_mode (bool | None): A Boolean value that determines whether only users that subscribe to the broadcaster’s channel can talk in the chat room
                Set to true, if the broadcaster restricts the chat room to subscribers only; otherwise, false
                Default is false
            unique_chat_mode (bool | None): A Boolean value that determines whether the broadcaster requires users to post only unique messages in the chat room
                Set to true, if the broadcaster requires unique messages only; otherwise, false
                Default is false

        Raises:
            errors.ClientError

        Returns:
            ChatSettings
        """

        return chats.update_chat_settings(
            self.__user_token,
            self.client_id,
            broadcaster_id,
            moderator_id,
            emote_mode,
            follower_mode,
            follower_mode_duration,
            non_moderator_chat_delay,
            non_moderator_chat_delay_duration,
            slow_mode,
            slow_mode_wait_time,
            subscriber_mode,
            unique_chat_mode,
        )

    def send_chat_announcement(
        self,
        broadcaster_id: str,
        moderator_id: str,
        message: str,
        color: str | None = None,
    ) -> None:
        """
        Sends an announcement to the broadcaster’s chat room

        Args:
            broadcaster_id (str): The ID of the broadcaster that owns the chat room to send the announcement to
            moderator_id (str): The ID of a user who has permission to moderate the broadcaster’s chat room, or the broadcaster’s ID if they’re sending the announcement
                This ID must match the user ID in the user access token
            message (str): The announcement to make in the broadcaster’s chat
                Announcements are limited to a maximum of 500 characters
            color (str | None): Announcements are limited to a maximum of 500 characters
                Possible case-sensitive values are: blue, green, orange, purple, primary (default)
                If color is set to primary or is not set, the channel’s accent color is used to highlight the announcement

        Raises:
            errors.ClientError
        """

        chats.send_chat_announcement(
            self.__user_token,
            self.client_id,
            broadcaster_id,
            moderator_id,
            message,
            color,
        )

    def send_a_shoutout(
        self, from_broadcaster_id: str, to_broadcaster_id: str, moderator_id: str
    ) -> None:
        """
        Sends a Shoutout to the specified broadcaster

        Args:
            from_broadcaster_id (str): The ID of the broadcaster that’s sending the Shoutout
            to_broadcaster_id (str): The ID of the broadcaster that’s receiving the Shoutout
            moderator_id (str): The ID of the broadcaster or a user that is one of the broadcaster’s moderators
                This ID must match the user ID in the access token

        Raises:
            errors.ClientError
        """

        chats.send_a_shoutout(
            self.__user_token,
            self.client_id,
            from_broadcaster_id,
            to_broadcaster_id,
            moderator_id,
        )

    def send_chat_message(
        self,
        broadcaster_id: str,
        sender_id: str,
        message: str,
        reply_parent_message_id: str | None = None,
    ) -> dict:
        """
        Sends a message to the broadcaster’s chat room

        Args:
            broadcaster_id (str): The ID of the broadcaster whose chat room the message will be sent to
            sender_id (str): The ID of the user sending the message
                This ID must match the user ID in the user access token
            message (str): The message to send
                The message is limited to a maximum of 500 characters
            reply_parent_message_id (str | None): The ID of the chat message being replied to

        Raises:
            errors.ClientError

        Returns:
            dict
        """

        return chats.send_chat_message(
            self.__app_token if self.__user_token == "" else self.__user_token,
            self.client_id,
            broadcaster_id,
            sender_id,
            message,
            reply_parent_message_id,
        )

    def get_user_chat_color(self, user_id: list[str]) -> list[tuple[User, str]]:
        """
        Gets the color used for the user’s name in chat

        Args:
            user_id (list[str]): The ID of the user whose username color you want to get
                Maximum: 100

        Raises:
            errors.ClientError

        Returns:
            list[tuple[User, str]]
        """

        return chats.get_user_chat_color(self.__app_token, self.client_id, user_id)

    def update_user_chat_color(self, user_id: str, color: str) -> None:
        """
        Updates the color used for the user’s name in chat

        Args:
            user_id (str): The ID of the user whose chat color you want to update
                This ID must match the user ID in the access token
            color (str): The color to use for the user’s name in chat
                All users may specify one of the following named color values: blue, blue_violet, cadet_blue, chocolate, coral, dodger_blue, firebrick, golden_rod, green, hot_pink, orange_red, red, sea_green, spring_green, yellow_green
                Turbo and Prime users may specify a named color or a Hex color code

        Raises:
            errors.ClientError
        """

        chats.update_user_chat_color(self.__user_token, self.client_id, user_id, color)

    def create_clip(
        self, broadcaster_id: str, has_delay: bool = False
    ) -> tuple[str, str]:
        """
        This returns both an ID and an edit URL for a new clip

        Args:
            broadcaster_id (str): ID of the stream from which the clip will be made
            has_delay (bool): If false, the clip is captured from the live stream when the API is called; otherwise, a delay is added before the clip is captured (to account for the brief delay between the broadcaster’s stream and the viewer’s experience of that stream)
                Default: false

        Raises:
            errors.ClientError

        Returns:
            tuple[str, str]
        """

        return clips.create_clip(
            self.__user_token, self.client_id, broadcaster_id, has_delay
        )

    def get_clips(
        self,
        broadcaster_id: str | None = None,
        game_id: str | None = None,
        clip_ids: list[str] | None = None,
        started_at: datetime | None = None,
        ended_at: datetime | None = None,
        first: int = 20,
        is_featured: bool | None = None,
    ) -> list[Clip]:
        """
        Gets one or more video clips that were captured from streams
        The id, game_id, and broadcaster_id query parameters are mutually exclusive

        Args:
            broadcaster_id (str | None): An ID that identifies the broadcaster whose video clips you want to get
            game_id (str | None): An ID that identifies the game whose clips you want to get
            clip_ids (list[str] | None): An ID that identifies the clip to get
            started_at (str | None): The start date used to filter clips
            ended_at (str | None): The end date used to filter clips
            first (int): The maximum number of clips to return
                Default: 20
            is_featured (bool | None): A Boolean value that determines whether the response includes featured clips

        Raises:
            errors.ClientError

        Returns:
            list[Clip]
        """

        return clips.get_clips(
            self.__user_token if self.__user_token != "" else self.__app_token,
            self.client_id,
            broadcaster_id,
            game_id,
            clip_ids,
            started_at,
            ended_at,
            first,
            is_featured,
        )

    def get_conduits(self) -> list[Conduit]:
        """
        Gets the conduits for a client ID

        Raises:
            errors.ClientError

        Returns:
            list[Conduit]
        """

        return eventsubs.get_conduits(self.__app_token, self.client_id)

    def create_conduits(self, shard_count: int) -> Conduit:
        """
        Creates a new conduit

        Args:
            shard_count (int): The number of shards to create for this conduit

        Raises:
            errors.ClientError

        Returns:
            Conduit
        """

        return eventsubs.create_conduits(self.__app_token, self.client_id, shard_count)

    def update_conduits(self, conduit_id: str, shard_count: int) -> Conduit:
        """
        Updates a conduit’s shard count
        To delete shards, update the count to a lower number, and the shards above the count will be deleted

        Args:
            conduit_id (str): Conduit ID
            shard_count (int): The new number of shards for this conduit

        Raises:
            errors.ClientError

        Returns:
            Conduit
        """

        return eventsubs.update_conduits(
            self.__app_token, self.client_id, conduit_id, shard_count
        )

    def delete_conduit(self, conduit_id: str) -> None:
        """
        Deletes a specified conduit

        Args:
            conduit_id (str): Conduit ID

        Raises:
            errors.ClientError
        """

        eventsubs.delete_conduit(self.__app_token, self.client_id, conduit_id)

    def get_conduit_shards(
        self, conduit_id: str, status: str | None = None
    ) -> list[ConduitShard]:
        """
        Gets a lists of all shards for a conduit

        Args:
            conduit_id (str): Conduit ID
            status (str | None): Status to filter by

        Raise:
            errors.ClientError

        Returns:
            list[ConduitShard]
        """

        return eventsubs.get_conduit_shards(
            self.__app_token, self.client_id, conduit_id, status
        )

    def update_conduit_shards(
        self, conduit_id: str, shards: list[ConduitShard], session_id: str | None = None
    ) -> list[ConduitShard]:
        """
        Updates shard(s) for a conduit

        Args:
            conduit_id (str): Conduit ID
            shards (list[ConduitShard]): List of shards to update
            session_id (str | None): An ID that identifies the WebSocket to send notifications to
                Specify this field only if method is set to websocket

        Raises:
            errors.ClientError

        Returns:
            list[ConduitShard]
        """

        return eventsubs.update_conduit_shards(
            self.__app_token, self.client_id, conduit_id, shards, session_id
        )

    def get_content_classification_labels(
        self, locale: str = "en-US"
    ) -> list[ContentClassificationLabel]:
        """
        Gets information about Twitch content classification labels

        Args:
            locale (str): Locale for the Content Classification Labels
                Possible values: "bg-BG", "cs-CZ", "da-DK", "da-DK", "de-DE", "el-GR", "en-GB", "en-US", "es-ES", "es-MX", "fi-FI", "fr-FR", "hu-HU", "it-IT", "ja-JP", "ko-KR", "nl-NL", "no-NO", "pl-PL", "pt-BT", "pt-PT", "ro-RO", "ru-RU", "sk-SK", "sv-SE", "th-TH", "tr-TR", "vi-VN", "zh-CN", "zh-TW"

        Raise:
            errors.ClientError

        Returns:
            list[ContentClassificationLabel]
        """

        return content_classification_labels.get_content_classification_labels(
            self.__user_token if self.__user_token != "" else self.__app_token,
            self.client_id,
            locale,
        )

    def get_drops_entitlements(
        self,
        entitlement_id: list[str] | None = None,
        user_id: str | None = None,
        game_id: str | None = None,
        fulfillment_status: str | None = None,
        first: int = 20,
    ) -> list[DropEntitlement]:
        """
        Gets a list of entitlements for a given organization that have been granted to a game, user, or both

        Args:
            entitlement_id (list[str] | None): ID of the entitlement
            user_id (str | None): A Twitch User ID
            game_id (str | None): A Twitch Game ID
            fulfillment_status (str | None): An optional fulfillment status used to filter entitlements
                Valid values are "CLAIMED" or "FULFILLED"
            first (int): Maximum number of entitlements to return
                Default: 20

        Raises:
            errors.ClientError

        Returns:
            list[DropEntitlement]
        """

        return drops.get_drops_entitlements(
            (
                self.__user_token
                if self.__user_token != "" and user_id is None
                else self.__app_token
            ),
            self.client_id,
            entitlement_id,
            user_id,
            game_id,
            fulfillment_status,
            first,
        )

    def update_drops_entitlements(
        self,
        entitlement_ids: list[str] | None = None,
        fulfillment_status: str | None = None,
    ) -> list[tuple[str, list[str]]]:
        """
        Updates the fulfillment status on a set of Drops entitlements, specified by their entitlement IDs

        Args:
            entitlement_ids (list[str] | None): An array of unique identifiers of the entitlements to update
                Maximum: 100
            fulfillment_status (str | None): A fulfillment status
                Valid values are "CLAIMED" or "FULFILLED"

        Raises:
            errors.ClientError

        Returns:
            list[tuple[str, list[str]]]
        """

        return drops.update_drops_entitlements(
            self.__user_token if self.__user_token != "" else self.__app_token,
            self.client_id,
            entitlement_ids,
            fulfillment_status,
        )

    def get_extension_configuration_segment(
        self, broadcaster_id: str, extension_id: str, segment: str
    ) -> ExtensionConfigurationSegment:
        """
        Gets the specified configuration segment from the specified extension
        You can retrieve each segment a maximum of 20 times per minute

        Args:
            broadcaster_id (str): The ID of the broadcaster for the configuration returned
                This parameter is required if you set the segment parameter to "broadcaster" or "developer"
                Do not specify this parameter if you set segment to "global"
            extension_id (str): The ID of the extension that contains the configuration segment you want to get
            segment (str): The type of configuration segment to get
                Valid values are: "broadcaster", "developer", "global"

        Raises:
            errors.ClientError

        Returns:
            ExtensionConfigurationSegment
        """

        return extensions.get_extension_configuration_segment(
            self.__jwt_token, self.client_id, broadcaster_id, extension_id, segment
        )

    def set_extension_configuration_segment(
        self,
        extension_id: str,
        segment: str,
        broadcaster_id: str | None = None,
        content: str | None = None,
        version: str | None = None,
    ) -> None:
        """
        Sets a single configuration segment of any type
        Each segment is limited to 5 KB and can be set at most 20 times per minute
        Updates to this data are not delivered to Extensions that have already been rendered

        Args:
            extension_id (str): ID for the Extension which the configuration is for
            segment (str): Configuration type
                Valid values are "global", "developer", or "broadcaster"
            broadcaster_id (str | None): User ID of the broadcaster
                Required if the segment type is "developer" or "broadcaster"
            content (str | None): Configuration in a string-encoded format
            version (str | None): Configuration version with the segment type

        Raises:
            errors.ClientError
        """

        extensions.set_extension_configuration_segment(
            self.__jwt_token,
            self.client_id,
            extension_id,
            segment,
            broadcaster_id,
            content,
            version,
        )

    def set_extension_required_configuration(
        self,
        broadcaster_id: str,
        extension_id: str,
        extension_version: str,
        configuration_version: str,
    ) -> None:
        """
        Enable activation of a specified Extension, after any required broadcaster configuration is correct

        Args:
            broadcaster_id (str): User ID of the broadcaster who has activated the specified Extension on their channel
            extension_id (str): ID for the Extension to activate
            extension_version (str): The version fo the Extension to release
            configuration_version (str): The version of the configuration to use with the Extension

        Raises:
            errors.ClientError
        """

        extensions.set_extension_required_configuration(
            self.__jwt_token,
            self.client_id,
            broadcaster_id,
            extension_id,
            extension_version,
            configuration_version,
        )

    def send_extension_pubsub_message(
        self,
        target: list[str],
        broadcaster_id: str,
        is_global_broadcast: bool,
        message: str,
    ) -> None:
        """
        A message can be sent to either a specified channel or globally (all channels on which your extension is active)
        Extension PubSub has a rate limit of 100 requests per minute for a combination of Extension client ID and broadcaster ID

        Args:
            target (list[str]): Array of strings for valid PubSub targets
                Valid values: "broadcast", "global", "whisper-<user-id>"
            broadcaster_id (str): ID of the broadcaster receiving the payload
            is_global_broadcast (bool): Indicates if the message should be sent to all channels where your Extension is active
            message (str): String-encoded JSON message to be sent

        Raises:
            errors.ClientError
        """

        extensions.send_extension_pubsub_message(
            self.__jwt_token,
            self.client_id,
            target,
            broadcaster_id,
            is_global_broadcast,
            message,
        )

    def get_extension_live_channels(
        self, extension_id: str, first: int = 20
    ) -> list[Channel]:
        """
        Returns one page of live channels that have installed or activated a specific Extension, identified by a client ID value assigned to the Extension when it is created
        A channel that recently went live may take a few minutes to appear in this list, and a channel may continue to appear on this list for a few minutes after it stops broadcasting

        Args:
            extension_id (str): ID of the Extension to search for
            first (int): Maximum number of objects to return
                Default: 20

        Raises:
            errors.ClientError

        Returns:
            list[Channel]
        """

        return extensions.get_extension_live_channels(
            self.__user_token if self.__user_token != "" else self.__app_token,
            self.client_id,
            extension_id,
            first,
        )

    def get_extension_secrets(self) -> list[tuple[str, list[ExtensionSecret]]]:
        """
        Retrieves a specified Extension’s secret data consisting of a version and an array of secret objects
        Each secret object contains a base64-encoded secret, a UTC timestamp when the secret becomes active, and a timestamp when the secret expires

        Raises:
            errors.ClientError

        Returns:
            list[tuple[str, list[ExtensionSecret]]]
        """

        return extensions.get_extension_secrets(self.__jwt_token, self.client_id)

    def create_extension_secret(
        self, delay: int = 300
    ) -> list[tuple[str, list[ExtensionSecret]]]:
        """
        Creates a JWT signing secret for a specific Extension
        Also rotates any current secrets out of service, with enough time for instances of the Extension to gracefully switch over to the new secret

        Args:
            delay (int): JWT signing activation delay for the newly created secret in seconds
                Minimum: 300
                Default: 300

        Raises:
            errors.ClientError

        Returns:
            list[tuple[str, list[ExtensionSecret]]]
        """

        return extensions.create_extension_secret(
            self.__jwt_token, self.client_id, delay
        )

    def send_extension_chat_message(
        self, broadcaster_id: str, text: str, extension_id: str, extension_version: str
    ) -> None:
        """
        Sends a specified chat message to a specified channel
        The message will appear in the channel’s chat as a normal message
        The "username" of the message is the Extension name
        There is a limit of 12 messages per minute, per channel

        Args:
            broadcaster_id (str): User ID of the broadcaster whose channel has the Extension activated
            text (str): Message for Twitch chat
                Maximum: 280 characters
            extension_id (str): Client ID associated with the Extension
            extension_version (str): Version of the Extension sending this message

        Raises:
            errors.ClientError
        """

        extensions.send_extension_chat_message(
            self.__jwt_token,
            self.client_id,
            broadcaster_id,
            text,
            extension_id,
            extension_version,
        )

    def get_extensions(
        self, extension_id: str, extension_version: str | None = None
    ) -> Extension:
        """
        Gets information about your Extensions; either the current version or a specified version

        Args:
            extension_id (str): ID of the Extension
            extension_version (str | None): The specific version of the Extension to return
                If not provided, the current version is returned

        Raises:
            errors.ClientError

        Returns:
            Extension
        """

        return extensions.get_extensions(
            self.__jwt_token, self.client_id, extension_id, extension_version
        )

    def get_released_extensions(
        self, extension_id: str, extension_version: str | None = None
    ) -> Extension:
        """
        Gets information about a released Extension; either the current version or a specified version

        Args:
            extension_id (str): ID of the Extension
            extension_version (str | None): The specific version of the Extension to return
                If not provided, the current version is returned

        Raises:
            errors.ClientError

        Returns:
            Extension
        """

        return extensions.get_released_extensions(
            self.__user_token if self.__user_token != "" else self.__app_token,
            self.client_id,
            extension_id,
            extension_version,
        )

    def get_extension_bits_products(
        self, extension_client_id: str, should_include_all: bool = False
    ) -> list[Product]:
        """
        Gets a list of Bits products that belongs to an Extension

        Args:
            extension_client_id (str): Extension client ID
            should_include_all (bool): Whether Bits products that are disabled/expired should be included in the response
                Default: false

        Raises:
            errors.ClientError

        Returns:
            list[Product]
        """

        return extensions.get_extension_bits_products(
            self.__app_token, extension_client_id, should_include_all
        )

    def update_extension_bits_product(
        self,
        extension_client_id: str,
        sku: str,
        cost: dict,
        display_name: str,
        in_development: bool | None = None,
        expiration: str | None = None,
        is_broadcast: bool | None = None,
    ) -> list[Product]:
        """
        Add or update a Bits products that belongs to an Extension

        Args:
            extension_client_id (str): Extension client ID
            sku (str): SKU of the Bits product
                This must be unique across all products that belong to an Extension
                The SKU cannot be changed after saving
                Maximum: 255 characters, no white spaces
            cost (dict): Object containing cost information
            display_name (str): Name of the product to be displayed in the Extension
                Maximum: 255 characters
            in_development (bool | None): Set to true if the product is in development and not yet released for public use
                Default: false
            expiration (str | None): Expiration time for the product in RFC3339 format
                If not provided, the Bits product will not have an expiration date
                Setting an expiration in the past will disable the product
            is_broadcast (bool | None): Indicates if Bits product purchase events are broadcast to all instances of an Extension on a channel via the “onTransactionComplete” helper callback
                Default: false

        Raises:
            errors.ClientError

        Returns:
            list[Product]
        """

        return extensions.update_extension_bits_product(
            self.__app_token,
            extension_client_id,
            sku,
            cost,
            display_name,
            in_development,
            expiration,
            is_broadcast,
        )

    def create_eventsub_subscription(
        self,
        subscription_type: str,
        version: str,
        condition: dict,
        transport: Transport,
    ) -> EventSubSubscription:
        """
        Creates an EventSub subscription

        Args:
            subscription_type (str): The category of the subscription that is being created
                Valid values: "channel.update", "channel.follow", "channel.subscribe", "channel.subscription.end", "channel.subscription.gift","channel.subscription.message", "channel.cheer", "channel.raid", "channel.ban", "channel.unban", "channel.moderator.add", "channel.moderator.remove", "channel.channel_points_custom_reward.add", "channel.channel_points_custom_reward.update", "channel.channel_points_custom_reward.remove", "channel.channel_points_custom_reward_redemption.add", "channel.channel_points_custom_reward_redemption.update", "channel.poll.begin", "channel.poll.progress", "channel.poll.end", "channel.prediction.begin", "channel.prediction.progress", "channel.prediction.lock", "channel.prediction.end", "drop.entitlement.grant", "extension.bits_transaction.create", "channel.hype_train.begin", "channel.hype_train.progress", "channel.hype_train.end", "stream.online", "stream.offline", "user.authorization.grant", "user.authorization.revoke", "user.update"
            version (str): The version of the subscription type that is being created
                Each subscription type has independent versioning
            condition (dict): Custom parameters for the subscription
            transport (Transport): Notification delivery specific configuration including a method string
                Valid transport methods include: webhook
                In addition to the method string, a webhook transport must include the callback and secret information

        Raises:
            errors.ClientError

        Returns:
            EventSubSubscription
        """

        return eventsubs.create_eventsub_subscription(
            self.__user_token if self.__user_token != "" else self.__app_token,
            self.client_id,
            subscription_type,
            version,
            condition,
            transport,
        )

    def delete_eventsub_subscription(self, subscription_id: str) -> None:
        """
        Delete an EventSub subscription

        Args:
            subscription_id (str): The subscription ID for the subscription to delete

        Raises:
            errors.ClientError
        """

        eventsubs.delete_eventsub_subscription(
            self.__user_token if self.__user_token != "" else self.__app_token,
            self.client_id,
            subscription_id,
        )

    def get_eventsub_subscriptions(
        self,
        status: str | None = None,
        subscription_type: str | None = None,
        user_id: str | None = None,
    ) -> list[EventSubSubscription]:
        """
        Get a list of your EventSub subscriptions
        Only include one filter query parameter

        Args:
            status (str | None): Filter subscriptions by its status
                Valid values: enabled, webhook_callback_verification_pending, webhook_callback_verification_failed, notification_failures_exceeded, authorization_revoked, moderator_removed, user_removed, chat_user_banned, version_removed, beta_maintenance, websocket_disconnected, websocket_failed_ping_pong, websocket_received_inbound_traffic, websocket_connection_unused, websocket_internal_error, websocket_network_timeout, websocket_network_error, websocket_failed_to_reconnect
            subscription_type (str | None): Filters subscriptions by subscription type name
            user_id (str | None): Filter subscriptions by user ID

        Raises:
            errors.ClientError

        Returns:
            list[EventSubSubscription]
        """

        return eventsubs.get_eventsub_subscriptions(
            self.__user_token if self.__user_token != "" else self.__app_token,
            self.client_id,
            status,
            subscription_type,
            user_id,
        )

    def get_top_games(self, first: int = 20) -> list[Game]:
        """
        Gets games sorted by number of current viewers on Twitch, most popular first

        Args:
            first (int): Maximum number of objects to return
                Default: 20

        Raises:
            errors.ClientError

        Returns:
            list[Game]
        """

        return games.get_top_games(
            self.__user_token if self.__user_token != "" else self.__app_token,
            self.client_id,
            first,
        )

    def get_games(
        self,
        game_id: list[str] | None = None,
        name: list[str] | None = None,
        igdb_id: list[str] | None = None,
    ) -> list[Game]:
        """
        Gets information about specified categories or games

        Args:
            game_id (list[str] | None): The ID of the category or game to get
                Maximum: 100
            name (list[str] | None): The name of the category or game to get
                Maximum: 100
            igdb_id (list[str] | None): The IGDB ID of the game to get
                Maximum: 100

        Raises:
            errors.ClientError

        Returns:
            list[Game]
        """

        return games.get_games(
            self.__user_token if self.__user_token != "" else self.__app_token,
            self.client_id,
            game_id,
            name,
            igdb_id,
        )

    def get_creator_goals(self, broadcaster_id: str) -> list[CreatorGoal]:
        """
        Gets the broadcaster’s list of active goals
        Use this to get the current progress of each goal

        Args:
            broadcaster_id (str): The ID of the broadcaster that created the goals

        Raises:
            errors.ClientError

        Returns:
            list[CreatorGoal]
        """

        return goals.get_creator_goals(
            self.__user_token, self.client_id, broadcaster_id
        )

    def get_channel_guest_star_settings(
        self, broadcaster_id: str, moderator_id: str
    ) -> GuestStarSettings:
        """
        Gets the channel settings for configuration of the Guest Star feature for a particular host

        Args:
            broadcaster_id (str): The ID of the broadcaster you want to get guest star settings for
            moderator_id (str): The ID of the broadcaster or a user that has permission to moderate the broadcaster’s chat room
                This ID must match the user ID in the user access token

        Raises:
            errors.ClientError

        Returns:
            GuestStarSettings
        """

        return guest_stars.get_channel_guest_star_settings(
            self.__user_token, self.client_id, broadcaster_id, moderator_id
        )

    def update_channel_guest_star_settings(
        self,
        broadcaster_id: str,
        is_moderator_send_live_enabled: bool | None = None,
        slot_count: int | None = None,
        is_browser_source_audio_enabled: bool | None = None,
        group_layout: str | None = None,
        regenerate_browser_sources: bool | None = None,
    ) -> None:
        """
        Mutates the channel settings for configuration of the Guest Star feature for a particular host

        Args:
            broadcaster_id (str): The ID of the broadcaster you want to update Guest Star settings for
            is_moderator_send_live_enabled (bool | None): Flag determining if Guest Star moderators have access to control whether a guest is live once assigned to a slot
            slot_count (int | None): Number of slots the Guest Star call interface will allow the host to add to a call.
                Required to be between 1 and 6
            is_browser_source_audio_enabled (bool | None): Flag determining if Browser Sources subscribed to sessions on this channel should output audio
            group_layout (str | None): This setting determines how the guests within a session should be laid out within the browser source
                Possible values: TILED_LAYOUT, SCREENSHARE_LAYOUT, HORIZONTAL_LAYOUT, VERTICAL_LAYOUT
            regenerate_browser_sources (bool | None): Flag determining if Guest Star should regenerate the auth token associated with the channel’s browser sources

        Raises:
            errors.ClientError
        """

        guest_stars.update_channel_guest_star_settings(
            self.__user_token,
            self.client_id,
            broadcaster_id,
            is_moderator_send_live_enabled,
            slot_count,
            is_browser_source_audio_enabled,
            group_layout,
            regenerate_browser_sources,
        )

    def get_guest_star_session(
        self, broadcaster_id: str, moderator_id: str
    ) -> GuestStarSession:
        """
        Gets information about an ongoing Guest Star session for a particular channel

        Args:
            broadcaster_id (str): ID for the user hosting the Guest Star session
            moderator_id (str): The ID of the broadcaster or a user that has permission to moderate the broadcaster’s chat room
                This ID must match the user ID in the user access token

        Raises:
            errors.ClientError

        Returns:
            GuestStarSession
        """

        return guest_stars.get_guest_star_session(
            self.__user_token, self.client_id, broadcaster_id, moderator_id
        )

    def create_guest_star_session(self, broadcaster_id: str) -> GuestStarSession:
        """
        Programmatically creates a Guest Star session on behalf of the broadcaster

        Args:
            broadcaster_id (str): The ID of the broadcaster you want to create a Guest Star session for
                Provided broadcaster_id must match the user_id in the auth token

        Raises:
            errors.ClientError

        Returns:
            GuestStarSession
        """

        return guest_stars.create_guest_star_session(
            self.__user_token, self.client_id, broadcaster_id
        )

    def end_guest_star_session(
        self, broadcaster_id: str, session_id: str
    ) -> GuestStarSession:
        """
        Programmatically ends a Guest Star session on behalf of the broadcaster

        Args:
            broadcaster_id (str): The ID of the broadcaster you want to end a Guest Star session for
                Provided broadcaster_id must match the user_id in the auth token
            session_id (str): ID for the session to end on behalf of the broadcaster

        Raises:
            errors.ClientError

        Returns:
            GuestStarSession
        """

        return guest_stars.end_guest_star_session(
            self.__user_token, self.client_id, broadcaster_id, session_id
        )

    def get_guest_star_invites(
        self, broadcaster_id: str, moderator_id: str, session_id: str
    ) -> list[GuestStarInvite]:
        """
        Provides a list of pending invites to a Guest Star session, including the invitee’s ready status while joining the waiting room

        Args:
            broadcaster_id (str): The ID of the broadcaster running the Guest Star session
            moderator_id (str): The ID of the broadcaster or a user that has permission to moderate the broadcaster’s chat room
                This ID must match the user_id in the user access token
            session_id (str): The session ID to query for invite status

        Raises:
            errors.ClientError

        Returns:
            list[GuestStarInvite]
        """

        return guest_stars.get_guest_star_invites(
            self.__user_token, self.client_id, broadcaster_id, moderator_id, session_id
        )

    def send_guest_star_invite(
        self, broadcaster_id: str, moderator_id: str, session_id: str, guest_id: str
    ) -> None:
        """
        Sends an invite to a specified guest on behalf of the broadcaster for a Guest Star session in progress

        Args:
            broadcaster_id (str): The ID of the broadcaster running the Guest Star session
            moderator_id (str): The ID of the broadcaster or a user that has permission to moderate the broadcaster’s chat room
                This ID must match the user_id in the user access token
            session_id (str): The session ID for the invite to be sent on behalf of the broadcaster
            guest_id (str): Twitch User ID for the guest to invite to the Guest Star session

        Raises:
            errors.ClientError
        """

        guest_stars.send_guest_star_invite(
            self.__user_token,
            self.client_id,
            broadcaster_id,
            moderator_id,
            session_id,
            guest_id,
        )

    def delete_guest_star_invite(
        self, broadcaster_id: str, moderator_id: str, session_id: str, guest_id: str
    ) -> None:
        """
        Revokes a previously sent invite for a Guest Star session

        Args:
            broadcaster_id (str): The ID of the broadcaster running the Guest Star session
            moderator_id (str): The ID of the broadcaster or a user that has permission to moderate the broadcaster’s chat room
                This ID must match the user_id in the user access token
            session_id (str): The ID of the session for the invite to be revoked on behalf of the broadcaster
            guest_id (str): Twitch User ID for the guest to revoke the Guest Star session invite from

        Raises:
            errors.ClientError
        """

        guest_stars.delete_guest_star_invite(
            self.__user_token,
            self.client_id,
            broadcaster_id,
            moderator_id,
            session_id,
            guest_id,
        )

    def assign_guest_star_slot(
        self,
        broadcaster_id: str,
        moderator_id: str,
        session_id: str,
        guest_id: str,
        slot_id: str,
    ) -> None:
        """
        Allows a previously invited user to be assigned a slot within the active Guest Star session, once that guest has indicated they are ready to join

        Args:
            broadcaster_id (str): The ID of the broadcaster running the Guest Star session
            moderator_id (str): The ID of the broadcaster or a user that has permission to moderate the broadcaster’s chat room
                This ID must match the user_id in the user access token
            session_id (str): The ID of the Guest Star session in which to assign the slot
            guest_id (str): The Twitch User ID corresponding to the guest to assign a slot in the session
                This user must already have an invite to this session, and have indicated that they are ready to join
            slot_id (str): The slot assignment to give to the user

        Raises:
            errors.ClientError
        """

        guest_stars.assign_guest_star_slot(
            self.__user_token,
            self.client_id,
            broadcaster_id,
            moderator_id,
            session_id,
            guest_id,
            slot_id,
        )

    def update_guest_star_slot(
        self,
        broadcaster_id: str,
        moderator_id: str,
        session_id: str,
        source_slot_id: str,
        destination_slot_id: str = "",
    ) -> None:
        """
        Allows a user to update the assigned slot for a particular user within the active Guest Star session

        Args:
            broadcaster_id (str): The ID of the broadcaster running the Guest Star session
            moderator_id (str): The ID of the broadcaster or a user that has permission to moderate the broadcaster’s chat room
                This ID must match the user_id in the user access token
            session_id (str): The ID of the Guest Star session in which to update slot settings
            source_slot_id (str): The slot assignment previously assigned to a user
            destination_slot_id (str): The slot to move this user assignment to
                If the destination slot is occupied, the user assigned will be swapped into source_slot_id

        Raises:
            errors.ClientError
        """

        guest_stars.update_guest_star_slot(
            self.__user_token,
            self.client_id,
            broadcaster_id,
            moderator_id,
            session_id,
            source_slot_id,
            destination_slot_id,
        )

    def delete_guest_star_slot(
        self,
        broadcaster_id: str,
        moderator_id: str,
        session_id: str,
        guest_id: str,
        slot_id: str,
        should_reinvite_guest: str = "",
    ) -> None:
        """
        Allows a caller to remove a slot assignment from a user participating in an active Guest Star session

        Args:
            broadcaster_id (str): The ID of the broadcaster running the Guest Star session
            moderator_id (str): The ID of the broadcaster or a user that has permission to moderate the broadcaster’s chat room
                This ID must match the user ID in the user access token
            session_id (str): The ID of the Guest Star session in which to remove the slot assignment
            guest_id (str): The Twitch User ID corresponding to the guest to remove from the session
            slot_id (str): The slot ID representing the slot assignment to remove from the session
            should_reinvite_guest (str): Flag signaling that the guest should be reinvited to the session, sending them back to the invite queue

        Raises:
            errors.ClientError
        """

        guest_stars.delete_guest_star_slot(
            self.__user_token,
            self.client_id,
            broadcaster_id,
            moderator_id,
            session_id,
            guest_id,
            slot_id,
            should_reinvite_guest,
        )

    def update_guest_star_slot_settings(
        self,
        broadcaster_id: str,
        moderator_id: str,
        session_id: str,
        slot_id: str,
        is_audio_enabled: bool | None = None,
        is_video_enabled: bool | None = None,
        is_live: bool | None = None,
        volume: int | None = None,
    ) -> None:
        """
        Allows a user to update slot settings for a particular guest within a Guest Star session, such as allowing the user to share audio or video within the call as a host

        Args:
            broadcaster_id (str): The ID of the broadcaster running the Guest Star session
            moderator_id (str): The ID of the broadcaster or a user that has permission to moderate the broadcaster’s chat room
                This ID must match the user ID in the user access token
            session_id (str): The ID of the Guest Star session in which to update a slot’s settings
            slot_id (str): The slot assignment that has previously been assigned to a user
            is_audio_enabled (bool | None): Flag indicating whether the slot is allowed to share their audio with the rest of the session
            is_video_enabled (bool | None): Flag indicating whether the slot is allowed to share their video with the rest of the session
            is_live (bool | None): Flag indicating whether the user assigned to this slot is visible/can be heard from any public subscriptions
            volume (int | None): Value from 0-100 that controls the audio volume for shared views containing the slot

        Raises:
            errors.ClientError
        """

        guest_stars.update_guest_star_slot_settings(
            self.__user_token,
            self.client_id,
            broadcaster_id,
            moderator_id,
            session_id,
            slot_id,
            is_audio_enabled,
            is_video_enabled,
            is_live,
            volume,
        )

    def get_hype_train_events(
        self, broadcaster_id: str, first: int = 1
    ) -> list[HypeTrainEvent]:
        """
        Gets the information of the most recent Hype Train of the given channel ID
        When there is currently an active Hype Train, it returns information about that Hype Train
        When there is currently no active Hype Train, it returns information about the most recent Hype Train
        After 5 days, if no Hype Train has been active, the endpoint will return an empty response

        Args:
            broadcaster_id (str): User ID of the broadcaster
                Must match the User ID in the Bearer token if User Token is used
            first (int): Maximum number of objects to return
                Default: 1

        Raises:
            errors.ClientError

        Returns:
            list[HypeTrainEvent]
        """

        return hype_trains.get_hype_train_events(
            self.__user_token, self.client_id, broadcaster_id, first
        )

    def check_automod_status(
        self, broadcaster_id: str, data: list[tuple[str, str]]
    ) -> list[tuple[str, bool]]:
        """
        Determines whether a string message meets the channel’s AutoMod requirements

        Args:
            broadcaster_id (str): Provided broadcaster_id must match the user_id in the auth token
            data (list[tuple[str, str]]): The list of messages to check
                Minimum: 1
                Maximum: 100

        Raises:
            errors.ClientError

        Returns:
            list[tuple[str, bool]]
        """

        return moderation.check_automod_status(
            self.__user_token, self.client_id, broadcaster_id, data
        )

    def manage_held_automod_messages(
        self, user_id: str, msg_id: str, action: str
    ) -> None:
        """
        Allow or deny a message that was held for review by AutoMod

        Args:
            user_id (str): The moderator who is approving or rejecting the held message
                Must match the user_id in the user OAuth token
            msg_id (str): ID of the message to be allowed or denied
            action (str): The action to take for the message
                Must be "ALLOW" or "DENY"

        Raises:
            errors.ClientError
        """

        moderation.manage_held_automod_messages(
            self.__user_token, self.client_id, user_id, msg_id, action
        )

    def get_automod_settings(
        self, broadcaster_id: str, moderator_id: str
    ) -> AutoModSettings:
        """
        Gets the broadcaster’s AutoMod settings, which are used to automatically block inappropriate or harassing messages from appearing in the broadcaster’s chat room

        Args:
            broadcaster_id (str): The ID of the broadcaster whose AutoMod settings you want to get
            moderator_id (str): The ID of a user that has permission to moderate the broadcaster’s chat room
                This ID must match the user ID associated with the user OAuth token
                If the broadcaster wants to get their own AutoMod settings (instead of having the moderator do it), set this parameter to the broadcaster’s ID, too

        Raises:
            errors.ClientError

        Returns:
            AutoModSettings
        """

        return moderation.get_automod_settings(
            self.__user_token, self.client_id, broadcaster_id, moderator_id
        )

    def update_automod_settings(
        self,
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
    ) -> AutoModSettings:
        """
        Updates the broadcaster’s AutoMod settings, which are used to automatically block inappropriate or harassing messages from appearing in the broadcaster’s chat room

        Args:
            broadcaster_id (str): The ID of the broadcaster whose AutoMod settings you want to update
            moderator_id (str): The ID of a user that has permission to moderate the broadcaster’s chat room
                This ID must match the user ID associated with the user OAuth token
                If the broadcaster wants to update their own AutoMod settings (instead of having the moderator do it), set this parameter to the broadcaster’s ID, too
            aggression (int | None): The Automod level for hostility involving aggression
            bullying (int | None): The Automod level for hostility involving name calling or insults
            disability (int | None): The Automod level for discrimination against disability
            misogyny (int | None): The Automod level for discrimination against women
            overall_level (int | None): The default AutoMod level for the broadcaster
            race_ethnicity_or_religion (int | None): The Automod level for racial discrimination
            sex_based_terms (int | None): The Automod level for sexual content
            sexuality_sex_or_gender (int | None): The AutoMod level for discrimination based on sexuality, sex, or gender
            swearing (int | None): The Automod level for profanity

        Raises:
            errors.ClientError

        Returns:
            AutoModSettings
        """

        return moderation.update_automod_settings(
            self.__user_token,
            self.client_id,
            broadcaster_id,
            moderator_id,
            aggression,
            bullying,
            disability,
            misogyny,
            overall_level,
            race_ethnicity_or_religion,
            sex_based_terms,
            sexuality_sex_or_gender,
            swearing,
        )

    def get_banned_users(
        self, broadcaster_id: str, user_id: list[str] | None = None, first: int = 20
    ) -> list[BannedUser]:
        """
        Returns all banned and timed-out users in a channel

        Args:
            broadcaster_id (str): Provided broadcaster_id must match the user_id in the auth token
            user_id (list | None): Filters the results and only returns a status object for users who are banned in this channel and have a matching user_id
                Maximum: 100
            first (int): Maximum number of objects to return
                Default: 20

        Raises:
            errors.ClientError

        Returns:
            list[BannedUser]
        """

        return moderation.get_banned_users(
            self.__user_token, self.client_id, broadcaster_id, user_id, first
        )

    def ban_user(
        self,
        broadcaster_id: str,
        moderator_id: str,
        reason: str,
        user_id: str,
        duration: int | None = None,
    ) -> dict:
        """
        Bans a user from participating in a broadcaster’s chat room, or puts them in a timeout
        If the user is currently in a timeout, you can use this method to change the duration of the timeout or ban them altogether
        If the user is currently banned, you cannot call this method to put them in a timeout instead

        Args:
            broadcaster_id (str): The ID of the broadcaster whose chat room the user is being banned from
            moderator_id (str): The ID of a user that has permission to moderate the broadcaster’s chat room
                This ID must match the user ID associated with the user OAuth token
                If the broadcaster wants to ban the user (instead of having the moderator do it), set this parameter to the broadcaster’s ID, too
            reason (str): The reason the user is being banned or put in a timeout
                The text is user defined and limited to a maximum of 500 characters
            user_id (str): The ID of the user to ban or put in a timeout
            duration (int | None): To ban a user indefinitely, don’t include this field
                To put a user in a timeout, include this field and specify the timeout period, in seconds
                The minimum timeout is 1 second and the maximum is 1,209,600 seconds (2 weeks)
                To end a user’s timeout early, set this field to 1

        Raises:
            errors.ClientError

        Returns:
            dict
        """

        return moderation.ban_user(
            self.__user_token,
            self.client_id,
            broadcaster_id,
            moderator_id,
            reason,
            user_id,
            duration,
        )

    def unban_user(self, broadcaster_id: str, moderator_id: str, user_id: str) -> None:
        """
        Removes the ban or timeout that was placed on the specified user

        Args:
            broadcaster_id (str): The ID of the broadcaster whose chat room the user is banned from chatting in
            moderator_id (str): The ID of a user that has permission to moderate the broadcaster’s chat room
                This ID must match the user ID associated with the user OAuth token
                If the broadcaster wants to remove the ban (instead of having the moderator do it), set this parameter to the broadcaster’s ID, too
            user_id (str): The ID of the user to remove the ban or timeout from

        Raises:
            errors.ClientError
        """

        return moderation.unban_user(
            self.__user_token, self.client_id, broadcaster_id, moderator_id, user_id
        )

    def get_unban_requests(
        self,
        broadcaster_id: str,
        moderator_id: str,
        status: str,
        user_id: str | None = None,
        first: int = 20,
    ) -> list[UnbanRequest]:
        """
        Gets a list of unban requests for a broadcaster’s channel

        Args:
            broadcaster_id (str): The ID of the broadcaster whose channel is receiving unban requests
            moderator_id (str): The ID of the broadcaster or a user that has permission to moderate the broadcaster’s unban requests
                This ID must match the user ID in the user access token
            status (str): Filter by a status
                Possible values: pending, approved, denied, acknowledged, canceled
            user_id (str | None): The ID used to filter what unban requests are returned
            first (int): The maximum number of items to return per page in response

        Raises:
            errors.ClientError

        Returns:
            list[UnbanRequest]
        """

        return moderation.get_unban_requests(
            self.__user_token,
            self.client_id,
            broadcaster_id,
            moderator_id,
            status,
            user_id,
            first,
        )

    def resolve_unban_requests(
        self,
        broadcaster_id: str,
        moderator_id: str,
        unban_request_id: str,
        status: str,
        resolution_text: str = "",
    ) -> UnbanRequest:
        """
        Resolves an unban request by approving or denying it.

        Args:
            broadcaster_id (str): The ID of the broadcaster whose channel is approving or denying the unban request
            moderator_id (str): The ID of the broadcaster or a user that has permission to moderate the broadcaster’s unban requests
                This ID must match the user ID in the user access token
            unban_request_id (str): The ID of the broadcaster or a user that has permission to moderate the broadcaster’s unban requests
                This ID must match the user ID in the user access token.
            status (str): Resolution status
                Possible values: approved, denied
            resolution_text (str): Message supplied by the unban request resolver
                The message is limited to a maximum of 500 characters.

        Raises:
            errors.ClientError

        Returns:
            UnbanRequest
        """

        return moderation.resolve_unban_requests(
            self.__user_token,
            self.client_id,
            broadcaster_id,
            moderator_id,
            unban_request_id,
            status,
            resolution_text,
        )

    def get_blocked_terms(
        self, broadcaster_id: str, moderator_id: str, first: int = 20
    ) -> list[BlockedTerm]:
        """
        Gets the broadcaster’s list of non-private, blocked words or phrases
        These are the terms that the broadcaster or moderator added manually, or that were denied by AutoMod

        Args:
            broadcaster_id (str): The ID of the broadcaster whose blocked terms you’re getting
            moderator_id (str): The ID of a user that has permission to moderate the broadcaster’s chat room
                This ID must match the user ID associated with the user OAuth token
                If the broadcaster wants to get their own block terms (instead of having the moderator do it), set this parameter to the broadcaster’s ID, too
            first (int): The maximum number of blocked terms to return per page in the response
                The minimum page size is 1 blocked term per page and the maximum is 100
                The default is 20

        Raises:
            errors.ClientError

        Returns:
            list[BlockedTerm]
        """

        return moderation.get_blocked_terms(
            self.__user_token, self.client_id, broadcaster_id, moderator_id, first
        )

    def add_blocked_term(
        self, broadcaster_id: str, moderator_id: str, text: str
    ) -> BlockedTerm:
        """
        Adds a word or phrase to the broadcaster’s list of blocked terms
        These are the terms that broadcasters don’t want used in their chat room

        Args:
            broadcaster_id (str): The ID of the broadcaster that owns the list of blocked terms
            moderator_id (str): The ID of a user that has permission to moderate the broadcaster’s chat room
                This ID must match the user ID associated with the user OAuth token
                If the broadcaster wants to add the blocked term (instead of having the moderator do it), set this parameter to the broadcaster’s ID, too
            text (str): The word or phrase to block from being used in the broadcaster’s chat room
                The term must contain a minimum of 2 characters and may contain up to a maximum of 500 characters
                Terms can use a wildcard character (*)
                The wildcard character must appear at the beginning or end of a word, or set of characters

        Raises:
            errors.ClientError

        Returns:
            BlockedTerm
        """

        return moderation.add_blocked_term(
            self.__user_token, self.client_id, broadcaster_id, moderator_id, text
        )

    def remove_blocked_term(
        self, broadcaster_id: str, blocked_term_id: str, moderator_id: str
    ) -> None:
        """
        Removes the word or phrase that the broadcaster is blocking users from using in their chat room

        Args:
            broadcaster_id (str): The ID of the broadcaster that owns the list of blocked terms
            blocked_term_id (str): The ID of the blocked term you want to delete
            moderator_id (str): The ID of a user that has permission to moderate the broadcaster’s chat room
                This ID must match the user ID associated with the user OAuth token
                If the broadcaster wants to delete the blocked term (instead of having the moderator do it), set this parameter to the broadcaster’s ID, too

        Raises:
            errors.ClientError
        """

        moderation.remove_blocked_term(
            self.__user_token,
            self.client_id,
            broadcaster_id,
            blocked_term_id,
            moderator_id,
        )

    def delete_chat_messages(
        self, broadcaster_id: str, moderator_id: str, message_id: str | None = None
    ) -> None:
        """
        Removes a single chat message or all chat messages from the broadcaster’s chat room

        Args:
            broadcaster_id (str): The ID of the broadcaster that owns the chat room to remove messages from
            moderator_id (str): The ID of the broadcaster or a user that has permission to moderate the broadcaster’s chat room
                This ID must match the user ID in the user access token
            message_id (str | None): The ID of the message to remove
                If not specified, the request removes all messages in the broadcaster’s chat room

        Raises:
            errors.ClientError
        """

        moderation.delete_chat_messages(
            self.__user_token, self.client_id, broadcaster_id, moderator_id, message_id
        )

    def get_moderated_channels(self, user_id: str, first: int = 20) -> list[Channel]:
        """
        Gets a list of channels that the specified user has moderator privileges in

        Args:
            user_id (str): A user’s ID
                This ID must match the user ID in the user OAuth token
            first (int): The number of items to return
                Default: 20

        Raises:
            errors.ClientError

        Returns:
            list[Channel]
        """

        return moderation.get_moderated_channels(
            self.__user_token, self.client_id, user_id, first
        )

    def get_moderators(
        self, broadcaster_id: str, user_id: list[str] | None = None, first: int = 20
    ) -> list[User]:
        """
        Returns all moderators in a channel

        Args:
            broadcaster_id (str): Provided broadcaster_id must match the user_id in the auth token
            user_id (list[str] | None): Filters the results and only returns a status object for users who are moderators in this channel and have a matching user_id
                Maximum: 100
            first (int): Maximum number of objects to return
                Default: 20

        Raises:
            errors.ClientError

        Returns:
            list[User]
        """

        return moderation.get_moderators(
            self.__user_token, self.client_id, broadcaster_id, user_id, first
        )

    def add_channel_moderator(self, broadcaster_id: str, user_id: str) -> None:
        """
        Adds a moderator to the broadcaster’s chat room

        Args:
            broadcaster_id (str): The ID of the broadcaster that owns the chat room
                This ID must match the user ID in the access token
            user_id (str): The ID of the user to add as a moderator in the broadcaster’s chat room

        Raises:
            errors.ClientError
        """

        moderation.add_channel_moderator(
            self.__user_token, self.client_id, broadcaster_id, user_id
        )

    def remove_channel_moderator(self, broadcaster_id: str, user_id: str) -> None:
        """
        Removes a moderator from the broadcaster’s chat room

        Args:
            broadcaster_id (str): The ID of the broadcaster that owns the chat room
                This ID must match the user ID in the access token
            user_id (str): The ID of the user to remove as a moderator from the broadcaster’s chat room

        Raises:
            errors.ClientError
        """

        moderation.remove_channel_moderator(
            self.__user_token, self.client_id, broadcaster_id, user_id
        )

    def get_vips(
        self, broadcaster_id: str, user_id: list[str] | None = None, first: int = 20
    ) -> list[User]:
        """
        Gets a list of the broadcaster’s VIPs

        Args:
            broadcaster_id (str): The ID of the broadcaster whose list of VIPs you want to get
                This ID must match the user ID in the access token
            user_id (list[str] | None): Filters the list for specific VIPs
                Maximum: 100
            first (int): The number of items to return
                Minimum: 1
                Maximum: 100

        Raises:
            errors.ClientError

        Returns:
            list[User]
        """

        return channels.get_vips(
            self.__user_token, self.client_id, broadcaster_id, user_id, first
        )

    def add_channel_vip(self, user_id: str, broadcaster_id: str) -> None:
        """
        Adds the specified user as a VIP in the broadcaster’s channel

        Args:
            user_id (str): The ID of the user to give VIP status to
            broadcaster_id (str): The ID of the broadcaster that’s adding the user as a VIP
                This ID must match the user ID in the access token

        Raises:
            errors.ClientError
        """

        channels.add_channel_vip(
            self.__user_token, self.client_id, user_id, broadcaster_id
        )

    def remove_channel_vip(self, user_id: str, broadcaster_id: str) -> None:
        """
        Removes the specified user as a VIP in the broadcaster’s channel

        Args:
            user_id (str): The ID of the user to remove VIP status from
            broadcaster_id (str): The ID of the user to remove VIP status from

        Raises:
            errors.ClientError
        """

        channels.remove_channel_vip(
            self.__user_token, self.client_id, user_id, broadcaster_id
        )

    def update_shield_mode_status(
        self, broadcaster_id: str, moderator_id: str, is_active: bool
    ) -> ShieldModeStatus:
        """
        Activates or deactivates the broadcaster’s Shield Mode

        Args:
            broadcaster_id (str): The ID of the broadcaster whose Shield Mode you want to activate or deactivate
            moderator_id (str): The ID of the broadcaster or a user that is one of the broadcaster’s moderators
                This ID must match the user ID in the access token
            is_active (bool): A Boolean value that determines whether to activate Shield Mode

        Raises:
            errors.ClientError

        Returns:
            ShieldModeStatus
        """

        return moderation.update_shield_mode_status(
            self.__user_token, self.client_id, broadcaster_id, moderator_id, is_active
        )

    def get_shield_mode_status(
        self, broadcaster_id: str, moderator_id: str
    ) -> ShieldModeStatus:
        """
        Gets the broadcaster’s Shield Mode activation status

        Args:
            broadcaster_id (str): The ID of the broadcaster whose Shield Mode activation status you want to get
            moderator_id (str): The ID of the broadcaster or a user that is one of the broadcaster’s moderators
                This ID must match the user ID in the access token

        Raises:
            errors.ClientError

        Returns:
            ShieldModeStatus
        """

        return moderation.get_shield_mode_status(
            self.__user_token, self.client_id, broadcaster_id, moderator_id
        )

    def warn_chat_user(
        self, broadcaster_id: str, moderator_id: str, user_id: str, reason: str
    ) -> ChatterWarning:
        """
        This function warns a user in a chat with a specified reason, using the provided broadcaster,
        moderator, and user IDs.

        Args:
            broadcaster_id (str): The ID of the channel in which the warning will take effect
            moderator_id (str): The ID of the Twitch user who requested the warning
            user_id (str): The ID of the Twitch user to be warned
            reason (str): A custom reason for the warning
                Maximum: 500 chars

        Raises:
            errors.ClientError

        Returns:
            ChatterWarning
        """

        return moderation.warn_chat_user(
            self.__user_token,
            self.client_id,
            broadcaster_id,
            moderator_id,
            user_id,
            reason,
        )

    def get_polls(
        self, broadcaster_id: str, poll_ids: list[str] | None = None, first: int = 20
    ) -> list[Poll]:
        """
        Gets a list of polls that the broadcaster created
        Polls are available for 90 days after they’re created

        Args:
            broadcaster_id (str): The ID of the broadcaster that created the polls
                This ID must match the user ID in the user access token
            poll_ids (list[str] | None): A list of IDs that identify the polls to return
                Maximum: 20
            first (int): The maximum number of items to return per page in the response
                Default: 20

        Raises:
            errors.ClientError

        Returns:
            list[Poll]
        """

        return polls.get_polls(
            self.__user_token, self.client_id, broadcaster_id, poll_ids, first
        )

    def create_poll(
        self,
        broadcaster_id: str,
        title: str,
        choices: list[str],
        duration: int,
        channel_points_voting_enabled: bool = False,
        channel_points_per_vote: int = 0,
    ) -> Poll:
        """
        Create a poll for a specific Twitch channel

        Args:
            broadcaster_id (str): The broadcaster running polls
                Provided broadcaster_id must match the user_id in the user OAuth token
            title (str): Question displayed for the poll
                Maximum: 60 characters
            choices (list[str]): Array of the poll choices
                Minimum: 2 choices
                Maximum: 5 choices
            duration (int): Total duration for the poll (in seconds)
                Minimum: 15
                Maximum: 1800
            channel_points_voting_enabled (bool): Indicates if Channel Points can be used for voting
                Default: false
            channel_points_per_vote (int): Number of Channel Points required to vote once with Channel Points
                Minimum: 0
                Maximum: 1000000

        Raises:
            errors.ClientError

        Returns:
            Poll
        """

        return polls.create_poll(
            self.__user_token,
            self.client_id,
            broadcaster_id,
            title,
            choices,
            duration,
            channel_points_voting_enabled,
            channel_points_per_vote,
        )

    def end_poll(self, broadcaster_id: str, poll_id: str, status: str) -> Poll:
        """
        Ends an active poll
        You have the option to end it or end it and archive it

        Args:
            broadcaster_id (str): The ID of the broadcaster that’s running the poll
                This ID must match the user ID in the user access token
            poll_id (str): The ID of the poll to update
            status (str): The status to set the poll to
                Valid values: "TERMINATED", "ARCHIVED"

        Raises:
            errors.ClientError

        Returns:
            Poll
        """

        return polls.end_poll(
            self.__user_token, self.client_id, broadcaster_id, poll_id, status
        )

    def get_predictions(
        self, broadcaster_id: str, prediction_ids: list[str] | None = None, first=20
    ) -> list[Prediction]:
        """
        Get information about all Channel Points Predictions or specific Channel Points Predictions for a Twitch channel

        Args:
            broadcaster_id (str): The broadcaster running Predictions
                Provided broadcaster_id must match the user_id in the user OAuth token
            prediction_ids (list | None): ID of a Prediction
                Maximum: 100
            first (int): Maximum number of objects to return
                Default: 20

        Raises:
            errors.ClientError

        Returns:
            list[Prediction]
        """

        return predictions.get_predictions(
            self.__user_token, self.client_id, broadcaster_id, prediction_ids, first
        )

    def create_prediction(
        self,
        broadcaster_id: str,
        title: str,
        outcomes: list[str],
        prediction_window: int,
    ) -> Prediction:
        """
        Create a Channel Points Prediction for a specific Twitch channel

        Args:
            broadcaster_id (str): The broadcaster running Predictions
                Provided broadcaster_id must match the user_id in the user OAuth token
            title (str): Title for the Prediction
                Maximum: 45 characters
            outcomes (list[str]): The list of possible outcomes that the viewers may choose from
                Minimum: 2
                Maximum: 10
            prediction_window (int): Total duration for the Prediction (in seconds)
                Minimum: 1
                Maximum: 1800

        Raises:
            errors.ClientError

        Returns:
            Prediction
        """

        return predictions.create_prediction(
            self.__user_token,
            self.client_id,
            broadcaster_id,
            title,
            outcomes,
            prediction_window,
        )

    def end_prediction(
        self,
        broadcaster_id: str,
        prediction_id: str,
        status: str,
        winning_outcome_id: str = "",
    ) -> Prediction:
        """
        Lock, resolve, or cancel a Channel Points Prediction
        Active Predictions can be updated to be "locked", "resolved", or "canceled"
        Locked Predictions can be updated to be "resolved" or "canceled"

        Args:
            broadcaster_id (str): The broadcaster running prediction events
                Provided broadcaster_id must match the user_id in the user OAuth token
            prediction_id (str): ID of the Prediction
            status (str): The Prediction status to be set
                Valid values: "RESOLVED", "CANCELED", "LOCKED"
            winning_outcome_id (str): ID of the winning outcome for the Prediction
                This parameter is required if status is being set to RESOLVED

        Raises:
            errors.ClientError

        Returns:
            Prediction
        """

        return predictions.end_prediction(
            self.__user_token,
            self.client_id,
            broadcaster_id,
            prediction_id,
            status,
            winning_outcome_id,
        )

    def start_raid(
        self, from_broadcaster_id: str, to_broadcaster_id: str
    ) -> tuple[datetime, bool]:
        """
        Raid another channel by sending the broadcaster’s viewers to the targeted channel

        Args:
            from_broadcaster_id (str): The ID of the broadcaster that’s sending the raiding party
                This ID must match the user ID in the user access token
            to_broadcaster_id (str): The ID of the broadcaster to raid

        Raises:
            errors.ClientError

        Returns:
            tuple[datetime, bool]
        """

        return raids.start_raid(
            self.__user_token, self.client_id, from_broadcaster_id, to_broadcaster_id
        )

    def cancel_raid(self, broadcaster_id: str) -> None:
        """
        Cancel a pending raid

        Args:
            broadcaster_id (str): The ID of the broadcaster that initiated the raid
                This ID must match the user ID in the user access token

        Raises:
            errors.ClientError
        """

        raids.cancel_raid(self.__user_token, self.client_id, broadcaster_id)

    def get_channel_stream_schedule(
        self,
        broadcaster_id: str,
        stream_segment_id: list[str] | None = None,
        start_time: datetime | None = None,
        first: int = 20,
    ) -> list[StreamSchedule]:
        """
        Gets all scheduled broadcasts or specific scheduled broadcasts from a channel’s stream schedule
        Scheduled broadcasts are defined as "stream segments"

        Args:
            broadcaster_id (str): User ID of the broadcaster who owns the channel streaming schedule
                Provided broadcaster_id must match the user_id in the user OAuth token
            stream_segment_id (list[str] | None): The ID of the stream segment to return
                Maximum: 100
            start_time (datetime | None): A timestamp in RFC3339 format to start returning stream segments from
                If not specified, the current date and time is used
            first (int): Maximum number of stream segments to return
                Default: 20

        Raises:
            errors.ClientError

        Returns:
            list[StreamSchedule]
        """

        return schedules.get_channel_stream_schedule(
            self.__user_token if self.__user_token != "" else self.__app_token,
            self.client_id,
            broadcaster_id,
            stream_segment_id,
            start_time,
            first,
        )

    def get_channel_icalendar(self, broadcaster_id: str) -> str:
        """
        Gets all scheduled broadcasts from a channel’s stream schedule as an iCalendar

        Args:
            broadcaster_id (str): User ID of the broadcaster who owns the channel streaming schedule

        Raises:
            errors.ClientError

        Returns:
            str
        """

        return schedules.get_channel_icalendar(broadcaster_id)

    def update_channel_stream_schedule(
        self,
        broadcaster_id: str,
        is_vacation_enabled: bool | None = None,
        vacation_start_time: datetime | None = None,
        vacation_end_time: datetime | None = None,
        timezone: str | None = None,
    ) -> None:
        """
        Update the settings for a channel’s stream schedule
        This can be used for setting vacation details

        Args:
            broadcaster_id (str): User ID of the broadcaster who owns the channel streaming schedule
                Provided broadcaster_id must match the user_id in the user OAuth token
            is_vacation_enabled (bool | None): Indicates if Vacation Mode is enabled
                Set to true to add a vacation or false to remove vacation from the channel streaming schedule
            vacation_start_time (str | None): Start time for vacation specified in RFC3339 format
                Required if is_vacation_enabled is set to true
            vacation_end_time (str | None): End time for vacation specified in RFC3339 format
                Required if is_vacation_enabled is set to true
            timezone (str | None): The timezone for when the vacation is being scheduled using the IANA time zone database format
                Required if is_vacation_enabled is set to true

        Raises:
            errors.ClientError
        """

        schedules.update_channel_stream_schedule(
            self.__user_token,
            self.client_id,
            broadcaster_id,
            is_vacation_enabled,
            vacation_start_time,
            vacation_end_time,
            timezone,
        )

    def create_channel_stream_schedule_segment(
        self,
        broadcaster_id: str,
        start_time: datetime,
        timezone: str,
        is_recurring: bool,
        duration: int = 240,
        category_id: str | None = None,
        title: str | None = None,
    ) -> StreamSchedule:
        """
        Create a single scheduled broadcast or a recurring scheduled broadcast for a channel’s stream schedule

        Args:
            broadcaster_id (str): User ID of the broadcaster who owns the channel streaming schedule
                Provided broadcaster_id must match the user_id in the user OAuth token
            start_time (datetime): Start time for the scheduled broadcast specified in RFC3339 format
            timezone (str): The timezone of the application creating the scheduled broadcast using the IANA time zone database format
            is_recurring (bool): Indicates if the scheduled broadcast is recurring weekly
            duration (int): Duration of the scheduled broadcast in minutes from the start_time
                Default: 240
            category_id (str | None): Game/Category ID for the scheduled broadcast
            title (str | None): Title for the scheduled broadcast
                Maximum: 140 characters

        Raises:
            errors.ClientError

        Returns:
            StreamSchedule
        """

        return schedules.create_channel_stream_schedule_segment(
            self.__user_token,
            self.client_id,
            broadcaster_id,
            start_time,
            timezone,
            is_recurring,
            duration,
            category_id,
            title,
        )

    def update_channel_stream_schedule_segment(
        self,
        broadcaster_id: str,
        stream_segment_id: str,
        start_time: datetime | None = None,
        duration: int | None = None,
        category_id: str | None = None,
        title: str | None = None,
        is_canceled: bool | None = None,
        timezone: str | None = None,
    ) -> StreamSchedule:
        """
        Update a single scheduled broadcast or a recurring scheduled broadcast for a channel’s stream schedule

        Args:
            broadcaster_id (str): User ID of the broadcaster who owns the channel streaming schedule
                Provided broadcaster_id must match the user_id in the user OAuth token
            stream_segment_id (str): The ID of the streaming segment to update
            start_time (datetime | None): Start time for the scheduled broadcast specified in RFC3339 format
            duration (int | None): Duration of the scheduled broadcast in minutes from the start_time
            category_id (str | None): Game/Category ID for the scheduled broadcast
            title (str | None): Title for the scheduled broadcast
                Maximum: 140 characters
            is_canceled (bool | None): Indicated if the scheduled broadcast is canceled
            timezone (str | None): The timezone of the application creating the scheduled broadcast using the IANA time zone database format

        Raises:
            errors.ClientError

        Returns:
            StreamSchedule
        """

        return schedules.update_channel_stream_schedule_segment(
            self.__user_token,
            self.client_id,
            broadcaster_id,
            stream_segment_id,
            start_time,
            duration,
            category_id,
            title,
            is_canceled,
            timezone,
        )

    def delete_channel_stream_schedule_segment(
        self, broadcaster_id: str, stream_segment_id: str
    ) -> None:
        """
        Delete a single scheduled broadcast or a recurring scheduled broadcast for a channel’s stream schedule

        Args:
            broadcaster_id (str): User ID of the broadcaster who owns the channel streaming schedule
                Provided broadcaster_id must match the user_id in the user OAuth token
            stream_segment_id (str): The ID of the streaming segment to delete

        Raises:
            errors.ClientError
        """

        schedules.delete_channel_stream_schedule_segment(
            self.__user_token, self.client_id, broadcaster_id, stream_segment_id
        )

    def search_categories(self, query: str, first: int = 20) -> list[Game]:
        """
        Returns a list of games or categories that match the query via name either entirely or partially

        Args:
            query (str): URI encoded search query
            first (int): Maximum number of objects to return
                Default: 20

        Raises:
            errors.ClientError

        Returns:
            list[Game]
        """

        return searchs.search_categories(
            self.__user_token if self.__user_token != "" else self.__app_token,
            self.client_id,
            query,
            first,
        )

    def search_channels(
        self, query: str, first: int = 20, live_only: bool = False
    ) -> list[Channel]:
        """
        Gets the channels that match the specified query and have streamed content within the past 6 months
        To match, the beginning of the broadcaster’s name or category must match the query string

        Args:
            query (str): The URI-encoded search string
            first (int): The maximum number of items to return
                Default: 20
            live_only (bool): A Boolean value that determines whether the response includes only channels that are currently streaming live

        Raises:
            errors.ClientError

        Returns:
            list[Channel]
        """

        return searchs.search_channels(
            self.__user_token if self.__user_token != "" else self.__app_token,
            self.client_id,
            query,
            first,
            live_only,
        )

    def get_stream_key(self, broadcaster_id: str) -> str:
        """
        Gets the channel stream key for a user

        Args:
            broadcaster_id (str): User ID of the broadcaster

        Raises:
            errors.ClientError

        Returns:
            str
        """

        return streams.get_stream_key(self.__user_token, self.client_id, broadcaster_id)

    def get_streams(
        self,
        user_id: list[str] | None = None,
        user_login: list[str] | None = None,
        game_id: list[str] | None = None,
        stream_type: str = "all",
        language: list[str] | None = None,
        first: int = 20,
    ) -> list[Stream]:
        """
        Gets a list of all streams
        The list is in descending order by the number of viewers watching the stream

        Args:
            user_id (list[str] | None): A user ID used to filter the list of streams
                Maximum: 100
            user_login (list[str] | None): A user login name used to filter the list of streams
                Maximum: 100
            game_id (list[str] | None): A game (category) ID used to filter the list of streams
                Maximum: 100
            stream_type (str): The type of stream to filter the list of streams by
                Possible values: all, live
            language (list[str] | None): A language code used to filter the list of streams
                Maximum: 100
            first (int): The maximum number of items to return
                Minimum: 1

        Raises:
            errors.ClientError

        Returns:
            list[Stream]
        """

        return streams.get_streams(
            self.__user_token if self.__user_token != "" else self.__app_token,
            self.client_id,
            user_id,
            user_login,
            game_id,
            stream_type,
            language,
            first,
        )

    def get_followed_streams(self, user_id: str, first: int = 100) -> list[Stream]:
        """
        Gets the list of broadcasters that the user follows and that are streaming live

        Args:
            user_id (str): The ID of the user whose list of followed streams you want to get
                This ID must match the user ID in the access token
            first (int): The maximum number of items to return
                Minimum: 1

        Raises:
            errors.ClientError

        Returns:
            list[Stream]
        """

        return streams.get_followed_streams(
            self.__user_token, self.client_id, user_id, first
        )

    def create_stream_marker(
        self, user_id: str, description: str | None = None
    ) -> StreamMarker:
        """
        Creates a marker in the stream of a user specified by user ID
        A marker is an arbitrary point in a stream that the broadcaster wants to mark; e.g., to easily return to later
        The marker is created at the current timestamp in the live broadcast when the request is processed

        Args:
            user_id (str): ID of the broadcaster in whose live stream the marker is created
            description (str | None): Description of or comments on the marker
                Max length is 140 characters

        Raises:
            errors.ClientError

        Returns:
            StreamMarker
        """

        return streams.create_stream_marker(
            self.__user_token, self.client_id, user_id, description
        )

    def get_stream_markers(
        self, user_id: str | None = None, video_id: str | None = None, first: int = 20
    ) -> list[dict]:
        """
        Gets a list of markers for either a specified user’s most recent stream or a specified VOD/video (stream)
        A marker is an arbitrary point in a stream that the broadcaster wants to mark; e.g., to easily return to later
        The only markers returned are those created by the user identified by the Bearer token
        Only one of user_id and video_id must be specified

        Args:
            user_id (str | None): ID of the broadcaster from whose stream markers are returned
            video_id (str | None): ID of the VOD/video whose stream markers are returned
            first (int): Number of values to be returned when getting videos by user or game ID
                Default: 20

        Raises:
            errors.ClientError

        Returns:
            list[dict]
        """

        return streams.get_stream_markers(
            self.__user_token, self.client_id, user_id, video_id, first
        )

    def get_broadcaster_subscriptions(
        self, broadcaster_id: str, user_id: list[str] | None = None, first: int = 20
    ) -> list[Subscription]:
        """
        Get all of a broadcaster’s subscriptions

        Args:
            broadcaster_id (str): User ID of the broadcaster
                Must match the User ID in the Bearer token
            user_id (list[str] | None): Filters results to only include potential subscriptions made by the provided user ID
                Accepts up to 100 values
            first (int): Maximum number of objects to return
                Default: 20

        Raises:
            errors.ClientError

        Returns:
            list[Subscription]
        """

        return subscriptions.get_broadcaster_subscriptions(
            self.__user_token, self.client_id, broadcaster_id, user_id, first
        )

    def check_user_subscription(
        self, broadcaster_id: str, user_id: str
    ) -> Subscription:
        """
        Checks if a specific user (user_id) is subscribed to a specific channel (broadcaster_id)

        Args:
            broadcaster_id (str): User ID of an Affiliate or Partner broadcaster
            user_id (str): User ID of a Twitch viewer

        Raises:
            errors.ClientError

        Returns:
            Subscription
        """

        return subscriptions.check_user_subscription(
            self.__user_token, self.client_id, broadcaster_id, user_id
        )

    def get_all_stream_tags(
        self, first: int = 20, tag_id: list[str] | None = None
    ) -> list[Tag]:
        """
        Gets the list of all stream tags defined by Twitch

        Args:
            first (int): Maximum number of objects to return
                Default: 20
            tag_id (list[str] | None): ID of a tag

        Raises:
            errors.ClientError

        Returns:
            list[Tag]
        """

        return tags.get_all_stream_tags(
            self.__user_token if self.__user_token != "" else self.__app_token,
            self.client_id,
            first,
            tag_id,
        )

    def get_stream_tags(self, broadcaster_id: str) -> list[Tag]:
        """
        Gets the list of current stream tags that have been set for a channel

        Args:
            broadcaster_id (str): User ID of the channel to get tags

        Raises:
            errors.ClientError

        Returns:
            list[Tag]
        """

        return tags.get_stream_tags(
            self.__user_token if self.__user_token != "" else self.__app_token,
            self.client_id,
            broadcaster_id,
        )

    def get_channel_teams(self, broadcaster_id: str) -> list[Team]:
        """
        Retrieves a list of Twitch Teams of which the specified channel/broadcaster is a member

        Args:
            broadcaster_id (str): User ID for a Twitch user

        Raises:
            errors.ClientError

        Returns:
            list[Team]
        """

        return teams.get_channel_teams(
            self.__user_token if self.__user_token != "" else self.__app_token,
            self.client_id,
            broadcaster_id,
        )

    def get_teams(self, name: str | None = None, team_id: str | None = None) -> Team:
        """
        Gets information for a specific Twitch Team
        One of the two optional query parameters must be specified to return Team information

        Args:
            name (str | None): Team name
            team_id (str | None): Team ID

        Raises:
            errors.ClientError

        Returns:
            Team
        """

        return teams.get_teams(
            self.__user_token if self.__user_token != "" else self.__app_token,
            self.client_id,
            name,
            team_id,
        )

    def get_users(
        self, user_ids: list[str] | None = None, login: list[str] | None = None
    ) -> list[User]:
        """
        Gets an user
        Users are identified by optional user IDs and/or login name
        If neither a user ID nor a login name is specified, the user is looked up by Bearer token

        Args:
            user_ids (list[str] | None): User ID
                Limit: 100
            login (list[str] | None): User login name
                Limit: 100

        Raises:
            errors.ClientError

        Returns:
            list[User]
        """

        return users.get_users(
            self.__user_token if self.__user_token != "" else self.__app_token,
            self.client_id,
            user_ids,
            login,
        )

    def update_user(self, description: str | None = None) -> User:
        """
        Updates the description of a user specified by the bearer token
        If the description parameter is not provided, no update will occur and the current user data is returned

        Args:
            description (str | None): User’s account description

        Raises:
            errors.ClientError

        Returns:
            User
        """

        return users.update_user(self.__user_token, self.client_id, description)

    def get_user_block_list(self, broadcaster_id: str, first: int = 20) -> list[User]:
        """
        Gets a specified user’s block list

        Args:
            broadcaster_id (str): User ID for a Twitch user
            first (int): Maximum number of objects to return
                Default: 20

        Raises:
            errors.ClientError

        Returns:
            list[User]
        """

        return users.get_user_block_list(
            self.__user_token, self.client_id, broadcaster_id, first
        )

    def block_user(
        self,
        target_user_id: str,
        source_context: str | None = None,
        reason: str | None = None,
    ) -> None:
        """
        Blocks the specified user on behalf of the authenticated user

        Args:
            target_user_id (str): User ID of the user to be blocked
            source_context (str | None): Source context for blocking the user
                Valid values: "chat", "whisper"
            reason (str | None): Reason for blocking the user
                Valid values: "spam", "harassment", or "other"

        Raises:
            errors.ClientError
        """

        users.block_user(
            self.__user_token, self.client_id, target_user_id, source_context, reason
        )

    def unblock_user(self, target_user_id: str) -> None:
        """
        Unblocks the specified user on behalf of the authenticated user

        Args:
            target_user_id (str): User ID of the user to be unblocked

        Raises:
            errors.ClientError
        """

        users.unblock_user(self.__user_token, self.client_id, target_user_id)

    def get_user_extensions(self) -> list[dict]:
        """
        Gets a list of all extensions (both active and inactive) for a specified user, identified by a Bearer token

        Raises:
            errors.ClientError

        Returns:
            list[dict]
        """

        return users.get_user_extensions(self.__user_token, self.client_id)

    def get_user_active_extensions(self, user_id: str | None = None) -> list[dict]:
        """
        Gets information about active extensions installed by a specified user, identified by a user ID or Bearer token

        Args:
            user_id (str | None): ID of the user whose installed extensions will be returned

        Raises:
            errors.ClientError

        Returns:
            list[dict]
        """

        return users.get_user_active_extensions(
            self.__user_token if self.__user_token != "" else self.__app_token,
            self.client_id,
            user_id,
        )

    def update_user_extensions(self, data: dict) -> list[dict]:
        """
        Updates the activation state, extension ID, and/or version number of installed extensions for a specified user, identified by a Bearer token
        If you try to activate a given extension under multiple extension types, the last write wins (and there is no guarantee of write order)

        Args:
            data (dict): The extensions to update
                The data field is a dictionary of extension types
                The dictionary’s possible keys are: panel, overlay, or component
                The key’s value is a dictionary of extensions
                For the extension’s dictionary, the key is a sequential number beginning with 1
                For panel and overlay extensions, the key’s value is an object that contains the following fields: active (true/false), id (the extension’s ID), and version (the extension’s version)
                For component extensions, the key’s value includes the above fields plus the x and y fields, which identify the coordinate where the extension is placed

        Raises:
            errors.ClientError

        Returns:
            list[dict]
        """

        return users.update_user_extensions(self.__user_token, self.client_id, data)

    def get_videos(
        self,
        video_ids: list[str] | None = None,
        user_id: str | None = None,
        game_id: str | None = None,
        first: int = 20,
        language: str | None = None,
        period: str = "all",
        sort: str = "time",
        video_type: str = "all",
    ) -> list[Video]:
        """
        Gets video information by video ID, user ID, or game ID
        Each request must specify one video id, one user_id, or one game_id

        Args:
            video_ids (list[str] | None): ID of the video being queried
                Limit: 100
                If this is specified, you cannot use first, language, period, sort and type
            user_id (str | None): ID of the user who owns the video
            game_id (str | None): ID of the game the video is of
            first (int): Number of values to be returned when getting videos by user or game ID
                Default: 20
            language (str | None): Language of the video being queried
                A language value must be either the ISO 639-1 two-letter code for a supported stream language or "other"
            period (str): Period during which the video was created
                Valid values: "all", "day", "week", "month"
            sort (str): Sort order of the videos
                Valid values: "time", "trending", "views"
                Default: "time"
            video_type (str): Type of video
                Valid values: "all", "upload", "archive", "highlight"
                Default: "all"

        Raises:
            errors.ClientError

        Returns:
            list[Video]
        """

        return videos.get_videos(
            self.__user_token if self.__user_token != "" else self.__app_token,
            self.client_id,
            video_ids,
            user_id,
            game_id,
            first,
            language,
            period,
            sort,
            video_type,
        )

    def delete_video(self, video_id: str) -> None:
        """
        Deletes a video
        Videos are past broadcasts, Highlights, or uploads

        Args:
            video_id (str): ID of the video(s) to be deleted
                Limit: 5

        Raises:
            errors.ClientError
        """

        videos.delete_video(self.__user_token, self.client_id, video_id)

    def send_whisper(self, from_user_id: str, to_user_id: str, message: str) -> None:
        """
        Sends a whisper message to the specified use

        Args:
            from_user_id (str): The ID of the user sending the whisper
                This user must have a verified phone number
                This ID must match the user ID in the user access token
            to_user_id (str): The ID of the user to receive the whisper
            message (str): The whisper message to send
                Maximum length: 500 characters if the user you're sending the message to hasn't whispered you before or 10,000 characters if the user you're sending the message to has whispered you before

        Raises:
            errors.ClientError
        """

        whispers.send_whisper(
            self.__user_token, self.client_id, from_user_id, to_user_id, message
        )
