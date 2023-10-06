import logging
import requests
from twitchpy.badge import Badge
from twitchpy.clip import Clip
from twitchpy.eventsub_subscription import EventSubSubscription
from twitchpy.extension import Extension
from twitchpy.hypetrain_event import HypeTrainEvent
from twitchpy.poll import Poll
from twitchpy.soundtrack_playlist import SoundtrackPlaylist
from twitchpy.soundtrack_track import SoundtrackTrack
from twitchpy.stream_schedule import StreamSchedule
from twitchpy.tag import Tag
from twitchpy.user import User
from twitchpy.game import Game
from twitchpy.stream import Stream
from twitchpy.channel import Channel
import os
from twitchpy.reward import Reward
from twitchpy.redemption import Redemption
import twitchpy.errors
import math
from twitchpy.video import Video
from twitchpy.team import Team
from twitchpy.emote import Emote
from twitchpy.prediction import Prediction
from twitchpy.charity_campaign import CharityCampaign
from twitchpy.charity_campaign_donation import CharityCampaignDonation

CONTENT_TYPE_APPLICATION_JSON = "application/json"
ENDPOINT_CUSTOM_REWARDS = "https://api.twitch.tv/helix/channel_points/custom_rewards"
ENDPOINT_EVENTSUB_SUBSCRIPTION = "https://api.twitch.tv/helix/eventsub/subscriptions"
ENDPOINT_MODERATION_BLOCKED_TERMS = "https://api.twitch.tv/helix/moderation/blocked_terms"
ENDPOINT_POLLS = "https://api.twitch.tv/helix/polls"
ENDPOINT_PREDICTIONS = "https://api.twitch.tv/helix/predictions"
ENDPOINT_SCHEDULE_SEGMENT = "https://api.twitch.tv/helix/schedule/segment"
ENDPOINT_USER_BLOCKS = "https://api.twitch.tv/helix/users/blocks"
ENDPOINT_VIPS = "https://api.twitch.tv/helix/channels/vips"

class Client:
    """
    Represents a client connection to the Twitch API
    """

    def __init__(self,oauth_token,client_id,client_secret,redirect_uri,tokens_path,code="",jwt_token=""):
        """
        Args:
            oauth_token (str): OAuth Token
            client_id (str): Client ID
            client_secret (str): Client secret
            redirect_uri (str): Redirect URI
            tokens_path (str): Path of tokens file (file included)
            code (str, optional): Authorization code for getting an user token
            jwt_token (str, optional): JWT Token
        """
        
        self.oauth_token=oauth_token
        self.client_id=client_id
        self.client_secret=client_secret
        self.redirect_uri=redirect_uri
        self.tokens_path=tokens_path
        self.__app_token=self.__get_app_token()

        if code!="":
            self.__user_token=self.__get_user_token(code)

        else:
            self.__user_token=""

        self.__jwt_token=jwt_token

    def __get_app_token(self):
        url="https://id.twitch.tv/oauth2/token"
        payload={"client_id":self.client_id,"client_secret":self.client_secret,"grant_type":"client_credentials"}

        response=requests.post(url,json=payload)

        if response.ok:
            return response.json()["access_token"]

        else:
            raise twitchpy.errors.AppTokenError("Error obtaining app token")

    def __is_last_code_used(self,code):
        try:
            tokens_file=open(self.tokens_path)
            tokens=tokens_file.readlines()
            tokens_file.close()
        
        except Exception:
            return False

        for token in tokens:
            token=token.replace(" ","").replace("\n","")
            token=token.split("=")

            if token[0]=="CODE" and token[1]==code:
                return True

        return False

    def __read_user_tokens_from_file(self,file):
        try:
            secret_file=open(file,"rt")
            data=secret_file.readlines()
            secret_file.close()

        except Exception as error:
            logging.exception("Error reading tokens")
            raise error

        user_token=""
        refresh_user_token=""

        for i in range(len(data)):
            secret=data[i].split("=")

            if "USER_TOKEN"==secret[0]:
                user_token=secret[1].replace("\n","")

            if "REFRESH_USER_TOKEN"==secret[0]:
                refresh_user_token=secret[1].replace("\n","")

        return user_token,refresh_user_token

    def __save_user_tokens_in_file(self,file,user_token,user_refresh_token,code):
        data=f"USER_TOKEN={user_token}\nREFRESH_USER_TOKEN={user_refresh_token}\nCODE={code}"

        secret_file=open(file,"wt")
        secret_file.write(data)
        secret_file.close()

    def __generate_user_tokens(self,code,file):
        url=f"https://id.twitch.tv/oauth2/token"
        payload={"client_id":self.client_id,"client_secret":self.client_secret,"code":code,"grant_type":"authorization_code","redirect_uri":self.redirect_uri}

        response=requests.post(url,payload)

        if response.ok:
            response=response.json()
            self.__save_user_tokens_in_file(file,response["access_token"],response["refresh_token"],code)

            return response["access_token"],response["refresh_token"]

        else:
            raise twitchpy.errors.ClientError(response.json()["message"])

    def __refresh_user_tokens(self,refresh_user_token):
        url="https://id.twitch.tv/oauth2/token"
        payload={"grant_type":"refresh_token","refresh_token":refresh_user_token,"client_id":self.client_id,"client_secret":self.client_secret}

        response=requests.post(url,json=payload)

        if response.ok:
            response=response.json()
            return response["access_token"],response["refresh_token"]

        else:
            raise twitchpy.errors.UserTokenError("Error obtaining user token")

    def __get_user_token(self,code):
        if self.__is_last_code_used(code) or (not self.__is_last_code_used(code) and os.path.isfile(self.tokens_path)):
            user_token,refresh_user_token=self.__read_user_tokens_from_file(self.tokens_path)
            user_token,refresh_user_token=self.__refresh_user_tokens(refresh_user_token)
            self.__save_user_tokens_in_file(self.tokens_path,user_token,refresh_user_token,code)

        else:
            user_token,refresh_user_token=self.__generate_user_tokens(code,self.tokens_path)

        return user_token

    def start_commercial(self,broadcaster_id,length):
        """
        Starts a commercial on a specified channel

        Args:
            broadcaster_id (int): ID of the channel requesting a commercial
            length (int): Desired length of the commercial in seconds
                          Valid options are 30, 60, 90, 120, 150 and 180

        Raises:
            twitchpy.errors.ClientError

        Returns:
            dict
        """

        url="https://api.twitch.tv/helix/channels/commercial"
        headers = {"Authorization": f"Bearer {self.__user_token}", "Client-Id": self.client_id, "Content-Type": CONTENT_TYPE_APPLICATION_JSON}
        payload={"broadcaster_id":broadcaster_id,"length":length}

        response=requests.post(url,headers=headers,json=payload)

        if response.ok:
            response=response.json()
            return response["data"][0]

        else:
            raise twitchpy.errors.ClientError(response.json()["message"])

    def get_extension_analytics(self,ended_at="",extension_id="",first=20,started_at="",type=""):
        """
        Gets a URL that Extension developers can use to download analytics reports for their Extensions
        The URL is valid for 5 minutes

        Args:
            ended_at (str, optional): Ending date/time for returned reports, in RFC3339 format with the hours, minutes, and seconds zeroed out and the UTC timezone: YYYY-MM-DDT00:00:00Z
                                      If this is provided, started_at also must be specified
            extension_id (str, optional): Client ID value assigned to the extension when it is created
            first (int, optional): Maximum number of objects to return
                                   Default: 20
            started_at (str, optional): Starting date/time for returned reports, in RFC3339 format with the hours, minutes, and seconds zeroed out and the UTC timezone: YYYY-MM-DDT00:00:00Z
                                        This must be on or after January 31, 2018
                                        If this is provided, ended_at also must be specified
            type (str, optional): Type of analytics report that is returned
                                  Valid values: "overview_v2"

        Raises:
            twitchpy.errors.ClientError

        Returns:
            list
        """

        url="https://api.twitch.tv/helix/analytics/extensions"
        headers={"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id}
        params={}

        if ended_at!="":
            params["ended_at"]=ended_at

        if extension_id!="":
            params["extension_id"]=extension_id

        if started_at!="":
            params["started_at"]=started_at

        if type!="":
            params["type"]=type

        after=""
        calls=math.ceil(first/100)
        extension_analytics=[]

        for call in range(calls):
            params["first"] = min(100, first-(100*call))

            if after!="":
                params["after"]=after

            response=requests.get(url,headers=headers,params=params)

            if response.ok:
                response=response.json()
                extension_analytics.extend(response["data"])

                if "pagination" in response:
                    after=response["pagination"]["cursor"]

            else:
                raise twitchpy.errors.ClientError(response.json()["message"])

        return extension_analytics

    def get_game_analytics(self,ended_at="",first=20,game_id="",started_at="",type=""):
        """
        Gets a URL that game developers can use to download analytics reports for their games
        The URL is valid for 5 minutes

        Args:
            ended_at (str, optional): Ending date/time for returned reports, in RFC3339 format with the hours, minutes, and seconds zeroed out and the UTC timezone: YYYY-MM-DDT00:00:00Z
                                      If this is provided, started_at also must be specified
            first (int, optional): Maximum number of objects to return
                                   Default: 20
            game_id (str, optional): Game ID
            started_at (str, optional): Starting date/time for returned reports, in RFC3339 format with the hours, minutes, and seconds zeroed out and the UTC timezone: YYYY-MM-DDT00:00:00Z
                                        If this is provided, ended_at also must be specified
            type (str, optional): Type of analytics report that is returned
                                  Valid values: "overview_v2"

        Raises:
            twitchpy.errors.ClientError

        Returns:
            list
        """

        url="https://api.twitch.tv/helix/analytics/games"
        headers={"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id}
        params={}

        if ended_at!="":
            params["ended_at"]=ended_at

        if game_id!="":
            params["game_id"]=game_id

        if started_at!="":
            params["started_at"]=started_at

        if type!="":
            params["type"]=type

        after=""
        calls=math.ceil(first/100)
        game_analytics=[]

        for call in range(calls):
            params["first"] = min(100, first-(100*call))

            if after!="":
                params["after"]=after

            response=requests.get(url,headers=headers,params=params)

            if response.ok:
                response=response.json()
                game_analytics.extend(response["data"])

                if "pagination" in response:
                    after=response["pagination"]["cursor"]

            else:
                raise twitchpy.errors.ClientError(response.json()["message"])

        return game_analytics

    def get_bits_leaderboard(self,count=10,period="all",started_at="",user_id=""):
        """
        Gets a ranked list of Bits leaderboard information for a broadcaster

        Args:
            count (int, optional): Number of results to be returned
                                   Maximum: 100
                                   Default: 10
            period (str, optional): Time period over which data is aggregated (PST time zone)
                                    This parameter interacts with started_at
                                    Default: "all"
                                    Valid values: "day", "week", "month", "year", "all"
            started_at (str, optional): Timestamp for the period over which the returned data is aggregated
                                        Must be in RFC 3339 format
                                        This value is ignored if period is "all"
            user_id (str, optional): ID of the user whose results are returned
                                     As long as count is greater than 1, the returned data includes additional users, with Bits amounts above and below the user specified

        Raises:
            twitchpy.errors.ClientError

        Returns:
            list
        """

        url="https://api.twitch.tv/helix/bits/leaderboard"
        headers={"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id}
        params={}

        if count!=10:
            params["count"]=count

        if period!="all":
            params["period"]=period

        if started_at!="":
            params["started_at"]=started_at

        if user_id!="":
            params["user_id"]=user_id

        response=requests.get(url,headers=headers,params=params)

        if response.ok:
            return response.json()["data"]

        else:
            raise twitchpy.errors.ClientError(response.json()["message"])

    def get_cheermotes(self,broadcaster_id=""):
        """
        Retrieves the list of available Cheermotes
        Cheermotes returned are available throughout Twitch, in all Bits-enabled channels

        Args:
            broadcaster_id (str, optional): ID for the broadcaster who might own specialized Cheermotes

        Raises:
            twitchpy.errors.ClientError

        Returns:
            list
        """

        url="https://api.twitch.tv/helix/bits/cheermotes"
        headers={"Authorization": f"Bearer {self.__app_token}","Client-Id":self.client_id}
        params={}

        if broadcaster_id!="":
            params={"broadcaster_id":broadcaster_id}
        
        response=requests.get(url,headers=headers,params=params)
        
        if response.ok:
            return response.json()["data"]

        else:
            raise twitchpy.errors.ClientError(response.json()["message"])
        
    def get_extension_transactions(self,extension_id,id=[],first=20):
        """
        Allows extension back-end servers to fetch a list of transactions that have occurred for their extension across all of Twitch
        A transaction is a record of a user exchanging Bits for an in-Extension digital good

        Args:
            extension_id (str): ID of the extension to list transactions for
            id (list, optional): Transaction IDs to look up
                                 Maximum: 100
            first (int, optional): Maximum number of objects to return
                                   Default: 20

        Raises:
            twitchpy.errors.ClientError

        Returns:
            list
        """

        url="https://api.twitch.tv/helix/extensions/transactions"
        headers={"Authorization": f"Bearer {self.__app_token}","Client-Id":self.client_id}
        params={"extension_id":extension_id}

        if len(id)>0:
            params["id"]=id

        if first!=20:
            params["first"]=first

        after=""
        calls=math.ceil(first/100)
        extension_transactions=[]

        for call in range(calls):
            if first-(100*call)>100:
                params["first"]=100
            
            else:
                params["first"]=first-(100*call)

            if after!="":
                params["after"]=after

            response=requests.get(url,headers=headers,params=params)

            if response.ok:
                response=response.json()
                extension_transactions.extend(response["data"])

                if "pagination" in response:
                    after=response["pagination"]["cursor"]

            else:
                raise twitchpy.errors.ClientError(response.json()["message"])

        return extension_transactions

    def get_channel(self, broadcaster_id: str | list[str]) -> Channel:
        """
        Gets a channel

        Args:
            broadcaster_id (str | list[str]): ID of the channel to be updated
                Maximum: 100

        Raises:
            twitchpy.errors.ClientError

        Returns:
            Channel
        """

        url="https://api.twitch.tv/helix/channels"
        headers={"Authorization": f"Bearer {self.__app_token}","Client-Id":self.client_id}
        params={"broadcaster_id":broadcaster_id}

        response=requests.get(url,headers=headers,params=params)

        if response.ok:
            channel=response.json()["data"][0]
            channel=Channel(channel["broadcaster_id"],channel["broadcaster_login"],channel["broadcaster_name"],channel["game_id"],channel["game_name"],channel["title"],channel["broadcaster_language"],channel["delay"])
            
            return channel

        else:
            raise twitchpy.errors.ClientError(response.json()["message"])

    def modify_channel_information(self,broadcaster_id,game_id="",broadcaster_language="",title="",delay=0):
        """
        Modifies channel information for users
        game_id, broadcaster_language, title and delay parameters are optional, but at least one parameter must be provided

        Args:
            broadcaster_id (str): ID of the channel to be updated
            game_id (str, optional): The current game ID being played on the channel
            broadcaster_language (str, optional): The language of the channel
                                                  A language value must be either the ISO 639-1 two-letter code for a supported stream language or “other”
            title (str, optional): The title of the stream
            delay (int ,optional): Stream delay in seconds
                                   Stream delay is a Twitch Partner feature

        Raises:
            twitchpy.errors.FewArgumentsError
        """

        url="https://api.twitch.tv/helix/channels"
        headers={"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id}
        data={"broadcaster_id":broadcaster_id}

        if game_id!="":
            data["game_id"]=game_id

        if broadcaster_language!="":
            data["broadcaster_language"]=broadcaster_language

        if title!="":
            data["title"]=title

        if delay!=0:
            data["delay"]=delay

        requests.patch(url,headers=headers,data=data)

    def get_channel_editors(self,broadcaster_id):
        """
        Gets a list of users who have editor permissions for a specific channel

        Args:
            broadcaster_id (str): Broadcaster’s user ID associated with the channel

        Raises:
            twitchpy.errors.ClientError

        Returns:
            list
        """

        url="https://api.twitch.tv/helix/channels/editors"
        headers={"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id}
        params={"broadcaster_id":broadcaster_id}

        response=requests.get(url,headers=headers,params=params)

        if response.ok:
            ids=[]

            for user in response.json()["data"]:
                ids.append(user["user_id"])

            users=self.get_users(id=ids)

            return users

        else:
            raise twitchpy.errors.ClientError(response.json()["message"])

    def create_custom_reward(self,broadcaster_id,title,cost,prompt="",is_enabled=True,background_color="",is_user_input_required=False,is_max_per_stream_enabled=False,max_per_stream=None,is_max_per_user_per_stream_enabled=False,max_per_user_per_stream=None,is_global_cooldown_enabled=False,global_cooldown_seconds=None,should_redemptions_skip_request_queue=False):
        """
        Creates a Custom Reward on a channel

        Args:
            broadcaster_id (str): ID of the channel creating a reward
            title (str): The title of the reward
            cost (int): The cost of the reward
            prompt (str, optional): The prompt for the viewer when they are redeeming the reward
            is_enabled (bool, optional): Is the reward currently enabled, if false the reward won’t show up to viewers
                                         Default: true
            background_color (str, optional): Custom background color for the reward
                                              Format: Hex with # prefix
            is_user_input_required (bool, optional): Does the user need to enter information when redeeming the reward
                                                     Default: false
            is_max_per_stream_enabled (bool, optional): Whether a maximum per stream is enabled
                                                        Default: false
            max_per_stream (int, optional): The maximum number per stream if enabled
                                            Required when any value of is_max_per_stream_enabled is included
            is_max_per_user_per_stream_enabled (bool, optional): Whether a maximum per user per stream is enabled
                                                                 Default: false
            max_per_user_per_stream (int, optional): The maximum number per user per stream if enabled
                                                     Required when any value of is_max_per_user_per_stream_enabled is included
            is_global_cooldown_enabled (bool, optional): Whether a cooldown is enabled
                                                         Default: false
            global_cooldown_seconds (int, optional): The cooldown in seconds if enabled
                                                     Required when any value of is_global_cooldown_enabled is included
            should_redemptions_skip_request_queue (bool, optional): Should redemptions be set to FULFILLED status immediately when redeemed and skip the request queue instead of the normal UNFULFILLED status
                                                                    Default: false

        Raises:
            twitchpy.errors.ClientError

        Returns:
            Reward
        """

        url = ENDPOINT_CUSTOM_REWARDS
        headers={"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id}
        params={"broadcaster_id":broadcaster_id,"title":title,"cost":cost}

        if prompt!="":
            params["prompt"]=prompt

        if is_enabled!=True:
            params["is_enabled"]=is_enabled

        if background_color!="":
            params["background_color"]=background_color

        if is_user_input_required!=False:
            params["is_user_input_required"]=is_user_input_required

        if is_max_per_stream_enabled!=False:
            params["is_max_per_stream_enabled"]=is_max_per_stream_enabled

        if max_per_stream!=None:
            params["max_per_stream"]=max_per_stream

        if is_max_per_user_per_stream_enabled!=False:
            params["is_max_per_user_per_stream_enabled"]=is_max_per_user_per_stream_enabled

        if max_per_user_per_stream!=None:
            params["max_per_user_per_stream"]=max_per_user_per_stream

        if is_global_cooldown_enabled!=False:
            params["is_global_cooldown_enabled"]=is_global_cooldown_enabled

        if global_cooldown_seconds!=None:
            params["global_cooldown_seconds"]=global_cooldown_seconds

        if should_redemptions_skip_request_queue!=False:
            params["should_redemptions_skip_request_queue"]=should_redemptions_skip_request_queue

        response=requests.post(url,headers=headers,params=params)

        if response.ok:
            reward=response.json()["data"][0]
            reward=Reward(reward["broadcaster_name"],reward["broadcaster_id"],reward["id"],image=reward["image"],background_color=reward["background_color"],is_enabled=reward["is_enabled"],cost=reward["cost"],title=reward["title"],prompt=reward["prompt"],is_user_input_required=reward["is_user_input_required"],max_per_stream_setting=reward["max_per_stream_setting"],max_per_user_per_stream_setting=reward["max_per_user_per_stream_setting"],global_cooldown_setting=reward["global_cooldown_setting"],is_paused=reward["is_paused"],is_in_stock=reward["is_in_stock"],default_image=reward["default_image"],should_redemptions_skip_request_queue=reward["should_redemptions_skip_request_queue"],redemptions_redeemed_current_stream=reward["redemptions_redeemed_current_stream"],cooldown_expires_at=reward["cooldown_expires_at"])

            return reward

        else:
            raise twitchpy.errors.ClientError(response.json()["message"])

    def delete_custom_reward(self,broadcaster_id,id):
        """
        Deletes a Custom Reward on a channel
        The Custom Reward specified by id must have been created by the client_id attached to the OAuth token in order to be deleted
        Any UNFULFILLED Custom Reward Redemptions of the deleted Custom Reward will be updated to the FULFILLED status

        Args:
            broadcaster_id (str): Provided broadcaster_id must match the user_id in the user OAuth token
            id (str): ID of the Custom Reward to delete
                      Must match a Custom Reward on broadcaster_id’s channel
        """

        url = ENDPOINT_CUSTOM_REWARDS
        headers={"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id}
        data={"broadcaster_id":broadcaster_id,"id":id}

        requests.delete(url,headers=headers,data=data)

    def get_custom_reward(self,broadcaster_id,id=[],only_manageable_rewards=False):
        """
        Returns a list of Custom Reward objects for the Custom Rewards on a channel

        Args:
            broadcaster_id (str): Provided broadcaster_id must match the user_id in the user OAuth token
            id (list, optional): This parameter filters the results and only returns reward objects for the Custom Rewards with matching ID
                                Maximum: 50
            only_manageable_rewards (bool, optional): When set to true, only returns custom rewards that the calling broadcaster can manage
                                                      Default: false

        Raises:
            twitchpy.errors.ClientError

        Returns:
            list
        """

        url=f"https://api.twitch.tv/helix/channel_points/custom_rewards"
        headers={"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id}
        params={"broadcaster_id":broadcaster_id}

        if len(id)>0:
            params["id"]=id

        if only_manageable_rewards!=False:
            params["only_manageable_rewards"]=only_manageable_rewards

        response=requests.get(url,headers=headers,params=params)

        if response.ok:
            rewards=[]

            for reward in response.json()["data"]:
                rewards.append(Reward(reward["broadcaster_name"],reward["broadcaster_id"],reward["id"],image=reward["image"],background_color=reward["background_color"],is_enabled=reward["is_enabled"],cost=reward["cost"],title=reward["title"],prompt=reward["prompt"],is_user_input_required=reward["is_user_input_required"],max_per_stream_setting=reward["max_per_stream_setting"],max_per_user_per_stream_setting=reward["max_per_user_per_stream_setting"],global_cooldown_setting=reward["global_cooldown_setting"],is_paused=reward["is_paused"],is_in_stock=reward["is_in_stock"],default_image=reward["default_image"],should_redemptions_skip_request_queue=reward["should_redemptions_skip_request_queue"],redemptions_redeemed_current_stream=reward["redemptions_redeemed_current_stream"],cooldown_expires_at=reward["cooldown_expires_at"]))

            return rewards

        else:
            raise twitchpy.errors.ClientError(response.json()["message"])

    def get_custom_reward_redemption(self,broadcaster_id,reward_id,id=[],status="",sort="OLDEST",first=20):
        """
        Returns Custom Reward Redemption objects for a Custom Reward on a channel that was created by the same client_id
        Developers only have access to get and update redemptions for the rewards created programmatically by the same client_id

        Args:
            broadcaster_id (str): Provided broadcaster_id must match the user_id in the user OAuth token
            reward_id (str): When ID is not provided, this parameter returns Custom Reward Redemption objects for redemptions of the Custom Reward with ID reward_id
            id (list, optional): When id is not provided, this param filters the results and only returns Custom Reward Redemption objects for the redemptions with matching ID
                                Maximum: 50
            status (str, optional): This param filters the Custom Reward Redemption objects for redemptions with the matching status
                                    Can be one of UNFULFILLED, FULFILLED or CANCELED
            sort (str, optional): Sort order of redemptions returned when getting the Custom Reward Redemption objects for a reward
                                  One of: OLDEST, NEWEST
                                  Default: OLDEST
            first (int, optional): Number of results to be returned when getting the Custom Reward Redemption objects for a reward
                                   Default: 20

        Raises:
            twitchpy.errors.ClientError

        Returns:
            list
        """

        url="https://api.twitch.tv/helix/channel_points/custom_rewards/redemptions"
        headers={"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id}
        params={"broadcaster_id":broadcaster_id,"reward_id":reward_id}

        if len(id)>0:
            params["id"]=id

        if status!="":
            params["status"]=status

        if sort!="OLDEST":
            params["sort"]=sort

        after=""
        calls=math.ceil(first/50)
        redemptions=[]

        for call in range(calls):
            params["first"] = min(50, first-(50*call))

            if after!="":
                params["after"]=after

            response=requests.get(url,headers=headers,params=params)

            if response.ok:
                for redemption in response.json()["data"]:
                    reward=Reward(redemption["broadcaster_name"],redemption["broadcaster_id"],redemption["reward"]["id"],cost=redemption["reward"]["cost"],title=redemption["reward"]["title"],prompt=redemption["reward"]["prompt"])
                    redemptions.append(Redemption(redemption["broadcaster_name"],redemption["broadcaster_id"],redemption["id"],redemption["user_id"],redemption["user_name"],redemption["user_input"],redemption["status"],redemption["redeemed_at"],reward))


            else:
                raise twitchpy.errors.ClientError(response.json()["message"])
        
        return redemptions

    def update_custom_reward(self,broadcaster_id,id,title="",prompt="",cost=None,background_color="",is_enabled=None,is_user_input_required=None,is_max_per_stream_enabled=None,max_per_stream=None,is_max_per_user_per_stream_enabled=None,max_per_user_per_stream=None,is_global_cooldown_enabled=None,global_cooldown_seconds=None,is_paused=None,should_redemptions_skip_request_queue=None):
        """
        Updates a Custom Reward created on a channel
        The Custom Reward specified by id must have been created by the client_id attached to the user OAuth token

        Args:
            broadcaster_id (str): Provided broadcaster_id must match the user_id in the user OAuth token
            id (str): ID of the Custom Reward to update
                      Must match a Custom Reward on the channel of the broadcaster_id
            title (str, optional): The title of the reward
            prompt (str, optional): The prompt for the viewer when they are redeeming the reward
            cost (int, optional): The cost of the reward
            background_color (str, optional): Custom background color for the reward as a hexadecimal value
            is_enabled (bool, optional): Is the reward currently enabled, if false the reward won’t show up to viewers
            is_user_input_required (bool, optional): Does the user need to enter information when redeeming the reward
            is_max_per_stream_enabled (bool, optional): Whether a maximum per stream is enabled
                                                        Required when any value of max_per_stream is included
            max_per_stream (int, optional): The maximum number per stream if enabled
                                            Required when any value of is_max_per_stream_enabled is included
            is_max_per_user_per_stream_enabled (bool, optional): Whether a maximum per user per stream is enabled
                                                                 Required when any value of max_per_user_per_stream is included
            max_per_user_per_stream (int, optional): The maximum number per user per stream if enabled
                                                     Required when any value of is_max_per_user_per_stream_enabled is included
            is_global_cooldown_enabled (bool, optional): Whether a cooldown is enabled
                                                         Required when any value of global_cooldown_seconds is included
            global_cooldown_seconds (int, optional): The cooldown in seconds if enabled
                                                     Required when any value of is_global_cooldown_enabled is included
            is_paused (bool, optional): Is the reward currently paused, if true viewers cannot redeem
            should_redemptions_skip_request_queue (bool, optional): Should redemptions be set to FULFILLED status immediately when redeemed and skip the request queue instead of the normal UNFULFILLED status

        Raises:
            twitchpy.errors.ClientError

        Returns:
            Reward
        """

        url = ENDPOINT_CUSTOM_REWARDS
        headers={"Authorization":f"Bearer {self.__user_token}","Client-Id":self.client_id}
        data={"broadcaster_id":broadcaster_id,"id":id}

        if title!="":
            data["title"]=title

        if prompt!="":
            data["prompt"]=prompt

        if cost!=None:
            data["cost"]=cost

        if background_color!="":
            data["background_color"]=background_color

        if is_enabled!=None:
            data["is_enabled"]=is_enabled

        if is_user_input_required!=None:
            data["is_user_input_required"]=is_user_input_required

        if is_max_per_stream_enabled!=None:
            data["is_max_per_stream_enabled"]=is_max_per_stream_enabled

        if max_per_stream!=None:
            data["max_per_stream"]=max_per_stream

        if is_max_per_user_per_stream_enabled!=None:
            data["is_max_per_user_per_stream_enabled"]=is_max_per_user_per_stream_enabled

        if max_per_user_per_stream!=None:
            data["max_per_user_per_stream"]=max_per_user_per_stream

        if is_global_cooldown_enabled!=None:
            data["is_global_cooldown_enabled"]=is_global_cooldown_enabled

        if global_cooldown_seconds!=None:
            data["global_cooldown_seconds"]=global_cooldown_seconds

        if is_paused!=None:
            data["is_paused"]=is_paused

        if should_redemptions_skip_request_queue!=None:
            data["should_redemptions_skip_request_queue"]=should_redemptions_skip_request_queue

        response=requests.patch(url,headers=headers,data=data)

        if response.ok:
            reward=response.json()["data"]
            reward=Reward(reward["broadcaster_name"],reward["broadcaster_id"],reward["id"],image=reward["image"],background_color=reward["background_color"],is_enabled=reward["is_enabled"],cost=reward["cost"],title=reward["title"],prompt=reward["prompt"],is_user_input_required=reward["is_user_input_required"],max_per_stream_setting=reward["max_per_stream_setting"],max_per_user_per_stream_setting=reward["max_per_user_per_stream_setting"],global_cooldown_setting=reward["global_cooldown_setting"],is_paused=reward["is_paused"],is_in_stock=reward["is_in_stock"],default_image=reward["default_image"],should_redemptions_skip_request_queue=reward["should_redemptions_skip_request_queue"],redemptions_redeemed_current_stream=reward["redemptions_redeemed_current_stream"],cooldown_expires_at=reward["cooldown_expires_at"])

            return reward

        else:
            raise twitchpy.errors.ClientError(response.json()["message"])

    def update_redemption_status(self,id,broadcaster_id,reward_id,status=""):
        """
        Updates the status of Custom Reward Redemption objects on a channel that are in the UNFULFILLED status
        The Custom Reward Redemption specified by id must be for a Custom Reward created by the client_id attached to the user OAuth token

        Args:
            id (list): ID of the Custom Reward Redemption to update
                      Must match a Custom Reward Redemption on broadcaster_id’s channel
                      Maximum: 50
            broadcaster_id (str): Provided broadcaster_id must match the user_id in the user OAuth token
            reward_id (str): ID of the Custom Reward the redemptions to be updated are for
            status (str, optional): The new status to set redemptions to
                                    Can be either FULFILLED or CANCELED
                                    Updating to CANCELED will refund the user their Channel Points

        Raises:
            twitchpy.errors.ClientError

        Returns:
            Redemption
        """

        url="https://api.twitch.tv/helix/channel_points/custom_rewards/redemptions"
        headers={"Authorization":f"Bearer {self.__user_token}","Client-Id":self.client_id}
        data={"id":id,"broadcaster_id":broadcaster_id,"reward_id":reward_id}

        if status!="":
            data["status"]=status

        response=requests.patch(url,headers=headers,data=data)

        if response.ok:
            redemption=response.json()["data"][0]
            reward=Reward(redemption["broadcaster_name"],redemption["broadcaster_id"],redemption["reward"]["id"],cost=redemption["reward"]["cost"],title=redemption["reward"]["title"],prompt=redemption["reward"]["prompt"])
            redemption=Redemption(redemption["broadcaster_name"],redemption["broadcaster_id"],redemption["id"],redemption["user_id"],redemption["user_name"],redemption["user_input"],redemption["status"],redemption["redeemed_at"],reward)
            
            return redemption

        else:
            raise twitchpy.errors.ClientError(response.json()["message"])

    def get_charity_campaign(self, broadcaster_id: str) -> CharityCampaign:
        """
        Gets information about the charity campaign that a broadcaster is running

        Args:
            broadcaster_id (str): The ID of the broadcaster that’s currently running a charity campaign
                This ID must match the user ID in the access token

        Raises:
            twitchpy.errors.ClientError

        Returns:
            CharityCampaign
        """

        url = "https://api.twitch.tv/helix/charity/campaigns"
        headers = {"Authorization": f"Bearer {self.__user_token}", "Client-Id": self.client_id}
        params = {"broadcaster_id": broadcaster_id}

        response = requests.get(url, headers=headers, params=params)

        if response.ok:
            return CharityCampaign(response.json()["data"][0]["id"], response.json()["data"][0]["broadcaster_id"], response.json()["data"][0]["broadcaster_name"], response.json()["data"][0]["broadcaster_login"], response.json()["data"][0]["charity_name"], response.json()["data"][0]["charity_description"], response.json()["data"][0]["charity_logo"], response.json()["data"][0]["charity_website"], response.json()["data"][0]["current_amount"], response.json()["data"][0]["target_amount"])

        else:
            raise twitchpy.errors.ClientError(response.json()["message"])

    def get_charity_campaign_donations(self, broadcaster_id: str, first: int = 20) -> list[CharityCampaignDonation]:
        """
        Gets the list of donations that users have made to the broadcaster’s active charity campaign

        Args:
            broadcaster_id (str): The ID of the broadcaster that’s currently running a charity campaign
                This ID must match the user ID in the access token
            first (int): The maximum number of items to return
                Default: 20
                Minimum: 1

        Raises:
            twitchpy.errors.ClientError

        Returns:
            list[CharityCampaignDonation]
        """

        url = "https://api.twitch.tv/helix/charity/donations"
        headers = {"Authorization": f"Bearer {self.__user_token}", "Client-Id": self.client_id}
        params = {"broadcaster_id": broadcaster_id}

        after = ""
        calls = math.ceil(first / 20)
        donations = []

        for call in range(calls):
            params["first"] = min(20, first - (20 * call))

            if after != "":
                params["after"] = after

            response = requests.get(url, headers=headers, params=params)

            if response.ok:
                response = response.json()

                for donation in response["data"]:
                    donations.append(CharityCampaignDonation(donation["id"], donation["campaign_id"], donation["user_id"], donation["user_login"], donation["user_name"], donation["amount"]))

                if "pagination" in response and "cursor" in response["pagination"]:
                    after = response["pagination"]["cursor"]

            else:
                raise twitchpy.errors.ClientError(response.json()["message"])

        return donations

    def get_chatters(self, broadcaster_id: str, moderator_id: str, first: int = 100) -> list[User]:
        """
        Gets the list of users that are connected to the broadcaster’s chat session

        Args:
            broadcaster_id (str): The ID of the broadcaster whose list of chatters you want to get
            moderator_id (str): The ID of the broadcaster or one of the broadcaster’s moderators
                This ID must match the user ID in the user access token
            first (int): The maximum number of items to return
                Default: 100
                Minimum: 1
                Maximum: 1000

        Raises:
            twitchpy.errors.ClientError

        Returns:
            list[User]
        """

        url = "https://api.twitch.tv/helix/chat/chatters"
        headers = {"Authorization": f"Bearer {self.__user_token}", "Client-Id": self.client_id}
        params = {"broadcaster_id": broadcaster_id, "moderator_id": moderator_id}

        after = ""
        calls = math.ceil(first / 100)
        users = []

        for call in range(calls):
            params["first"] = min(100, first - (100 * call))

            if after != "":
                params["after"] = after

            response = requests.get(url, headers=headers, params=params)

            if response.ok:
                response = response.json()

                users.extend(self.get_users([user["user_id"] for user in response["data"]]))

                if "pagination" in response and "cursor" in response["pagination"]:
                    after = response["pagination"]["cursor"]

            else:
                raise twitchpy.errors.ClientError(response.json()["message"])

        return users

    def get_channel_emotes(self,broadcaster_id):
        """
        Gets all custom emotes for a specific Twitch channel including subscriber emotes, Bits tier emotes, and follower emotes
        Custom channel emotes are custom emoticons that viewers may use in Twitch chat once they are subscribed to, cheered in, or followed the channel that owns the emotes

        Args:
            broadcaster_id (str): The broadcaster whose emotes are being requested

        Raises:
            twitchpy.errors.ClientError

        Returns:
            list
        """

        url="https://api.twitch.tv/helix/chat/emotes"
        headers={"Authorization":f"Bearer {self.__app_token}","Client-Id":self.client_id}
        params={"broadcaster_id":broadcaster_id}

        response=requests.get(url,headers=headers,params=params)

        if response.ok:
            emotes=[]

            for emote in response.json()["data"]:
                emotes.append(Emote(emote["id"],emote["name"],emote["images"],emote["format"],emote["scale"],emote["theme_mode"],emote["tier"],emote["emote_type"],emote["emote_set_id"]))

            return emotes

        else:
            raise twitchpy.errors.ClientError(response.json()["message"])

    def get_global_emotes(self):
        """
        Gets all global emotes
        Global emotes are Twitch-specific emoticons that every user can use in Twitch chat

        Raises:
            twitchpy.errors.ClientError

        Returns:
            list
        """

        url="https://api.twitch.tv/helix/chat/emotes/global"
        headers={"Authorization":f"Bearer {self.__app_token}","Client-Id":self.client_id}

        response=requests.get(url,headers=headers)

        if response.ok:
            emotes=[]

            for emote in response.json()["data"]:
                emotes.append(Emote(emote["id"],emote["name"],emote["images"],emote["format"],emote["scale"],emote["theme_mode"]))

            return emotes

        else:
            raise twitchpy.errors.ClientError(response.json()["message"])

    def get_emote_sets(self,emote_set_id):
        """
        Gets all Twitch emotes for one or more specific emote sets

        Args:
            emote_set_id (list): ID(s) of the emote set
                                 Maximum: 25

        Raises:
            twitchpy.errors.ClientError

        Returns:
            list
        """

        url="https://api.twitch.tv/helix/chat/emotes/set"
        headers={"Authorization":f"Bearer {self.__app_token}","Client-Id":self.client_id}
        params={"emote_set_id":emote_set_id}

        response=requests.get(url,headers=headers,params=params)

        if response.ok:
            emotes=[]

            for emote in response.json()["data"]:
                emotes.append(Emote(emote["id"],emote["name"],emote["images"],emote["format"],emote["scale"],emote["theme_mode"],emote_type=emote["emote_type"],emote_set_id=emote["emote_set_id"]))

            return emotes

        else:
            raise twitchpy.errors.ClientError(response.json()["message"])

    def get_channel_chat_badges(self,broadcaster_id):
        """
        Gets a list of custom chat badges that can be used in chat for the specified channel
        This includes subscriber badges and Bit badges

        Args:
            broadcaster_id (str): The broadcaster whose chat badges are being requested
                                  Provided broadcaster_id must match the user_id in the user OAuth token

        Raises:
            twitchpy.errors.ClientError

        Returns:
            list
        """

        url="https://api.twitch.tv/helix/chat/badges"
        headers={"Authorization":f"Bearer {self.__app_token}","Client-Id":self.client_id}
        params={"broadcaster_id":broadcaster_id}

        response=requests.get(url,headers=headers,params=params)
        
        if response.ok:
            badges=[]

            for badge in response.json()["data"]:
                badges.append(Badge(badge["set_id"],badge["versions"]))

            return badges

        else:
            raise twitchpy.errors.ClientError(response.json()["message"])

    def get_global_chat_badges(self):
        """
        Gets a list of chat badges that can be used in chat for any channel

        Raises:
            twitchpy.errors.ClientError

        Returns:
            list
        """

        url="https://api.twitch.tv/helix/chat/badges/global"
        headers={"Authorization":f"Bearer {self.__app_token}","Client-Id":self.client_id}

        response=requests.get(url,headers=headers)
        
        if response.ok:
            badges=[]

            for badge in response.json()["data"]:
                badges.append(Badge(badge["set_id"],badge["versions"]))

            return badges

        else:
            raise twitchpy.errors.ClientError(response.json()["message"])

    def get_chat_settings(self,broadcaster_id,moderator_id=""):
        """
        Gets the broadcaster’s chat settings

        Args:
            broadcaster_id (str): The ID of the broadcaster whose chat settings you want to get
            moderator_id (str, optional): Required only to access the non_moderator_chat_delay or non_moderator_chat_delay_duration settings
                                          The ID of a user that has permission to moderate the broadcaster’s chat room
                                          This ID must match the user ID associated with the user OAuth token
                                          If the broadcaster wants to get their own settings (instead of having the moderator do it), set this parameter to the broadcaster’s ID, too

        Raises:
            twitchpy.errors.ClientError

        Returns:
            dict
        """

        url="https://api.twitch.tv/helix/chat/settings"
        headers={"Authorization":f"Bearer {self.__user_token}","Client-Id":self.client_id}
        params={"broadcaster_id":broadcaster_id,"moderator_id":moderator_id}

        response=requests.get(url,headers=headers,params=params)

        if response.ok:
            return response.json()["data"][0]

        else:
            raise twitchpy.errors.ClientError(response.json()["message"])

    def update_chat_settings(self,broadcaster_id,moderator_id,emote_mode=None,follower_mode=None,follower_mode_duration=0,non_moderator_chat_delay=None,non_moderator_chat_delay_duration=0,slow_mode=None,slow_mode_wait_time=30,subscriber_mode=None,unique_chat_mode=None):
        """
        Updates the broadcaster’s chat settings

        Args:
            broadcaster_id (str): The ID of the broadcaster whose chat settings you want to update
                                  This ID must match the user ID associated with the user OAuth token
            moderator_id (str): The ID of a user that has permission to moderate the broadcaster’s chat room
                                This ID must match the user ID associated with the user OAuth token
                                If the broadcaster wants to update their own settings (instead of having the moderator do it), set this parameter to the broadcaster’s ID, too
            emote_mode (bool, optional): A Boolean value that determines whether chat messages must contain only emotes
                                         Set to true, if only messages that are 100% emotes are allowed; otherwise, false
                                         Default is false
            follower_mode (bool, optional): A Boolean value that determines whether the broadcaster restricts the chat room to followers only, based on how long they’ve followed
                                            Set to true, if the broadcaster restricts the chat room to followers only; otherwise, false
                                            Default is false
            follower_mode_duration (int, optional): The length of time, in minutes, that the followers must have followed the broadcaster to participate in the chat room
                                                    You may specify a value in the range: 0 (no restriction) through 129600 (3 months)
                                                    The default is 0
            non_moderator_chat_delay (bool, optional): A Boolean value that determines whether the broadcaster adds a short delay before chat messages appear in the chat room
                                                       This gives chat moderators and bots a chance to remove them before viewers can see the message
                                                       Set to true, if the broadcaster applies a delay; otherwise, false
                                                       Default is false
            non_moderator_chat_delay_duration (int, optional): The amount of time, in seconds, that messages are delayed from appearing in chat
                                                               Possible values are: 2, 4, 6
            slow_mode (bool, optional): A Boolean value that determines whether the broadcaster limits how often users in the chat room are allowed to send messages
                                        Set to true, if the broadcaster applies a wait period messages; otherwise, false
                                        Default is false
            slow_mode_wait_time (int, optional): The amount of time, in seconds, that users need to wait between sending messages
                                                 You may specify a value in the range: 3 (3 second delay) through 120 (2 minute delay)
                                                 The default is 30 seconds
            subscriber_mode (bool, optional): A Boolean value that determines whether only users that subscribe to the broadcaster’s channel can talk in the chat room
                                              Set to true, if the broadcaster restricts the chat room to subscribers only; otherwise, false
                                              Default is false
            unique_chat_mode (bool, optional): A Boolean value that determines whether the broadcaster requires users to post only unique messages in the chat room
                                               Set to true, if the broadcaster requires unique messages only; otherwise, false
                                               Default is false

        Raises:
            twitchpy.errors.ClientError

        Returns:
            dict
        """

        url="https://api.twitch.tv/helix/chat/settings"
        headers={"Authorization":f"Bearer {self.__user_token}","Client-Id":self.client_id}
        data={"broadcaster_id":broadcaster_id,"moderator_id":moderator_id}

        if emote_mode!=None:
            data["emote_mode"]=emote_mode
        
        if follower_mode!=None:
            data["follower_mode"]=follower_mode
        
        if follower_mode_duration!=0:
            data["follower_mode_duration"]=follower_mode_duration

        if non_moderator_chat_delay!=None:
            data["non_moderator_chat_delay"]=non_moderator_chat_delay

        if non_moderator_chat_delay_duration!=0:
            data["non_moderator_chat_delay_duration"]=non_moderator_chat_delay_duration

        if slow_mode!=None:
            data["slow_mode"]=slow_mode

        if slow_mode_wait_time!=30:
            data["slow_mode_wait_time"]=slow_mode_wait_time

        if subscriber_mode!=None:
            data["subscriber_mode"]=subscriber_mode

        if unique_chat_mode!=None:
            data["unique_chat_mode"]=unique_chat_mode

        response=requests.patch(url,headers=headers,data=data)

        if response.ok:
            return response.json()["data"][0]

        else:
            raise twitchpy.errors.ClientError(response.json()["message"])

    def send_chat_announcement(self, broadcaster_id: str, moderator_id: str, message: str, color: str = "") -> None:
        """
        Sends an announcement to the broadcaster’s chat room

        Args:
            broadcaster_id (str): The ID of the broadcaster that owns the chat room to send the announcement to
            moderator_id (str): The ID of a user who has permission to moderate the broadcaster’s chat room, or the broadcaster’s ID if they’re sending the announcement
                This ID must match the user ID in the user access token
            message (str): The announcement to make in the broadcaster’s chat
                Announcements are limited to a maximum of 500 characters
            color (str): Announcements are limited to a maximum of 500 characters
                Possible case-sensitive values are: blue, green, orange, purple, primary (default)
                If color is set to primary or is not set, the channel’s accent color is used to highlight the announcement
        """

        url = "https://api.twitch.tv/helix/chat/announcements"
        headers = {"Authorization": f"Bearer {self.__user_token}", "Client-Id": self.client_id, "Content-Type": "application/json"}
        payload = {"broadcaster_id": broadcaster_id, "moderator_id": moderator_id, "message": message}

        if color != "":
            payload["color"] = color

        requests.post(url, headers=headers, json=payload)

    def get_user_chat_color(self, user_id: str | list[str]) -> list[dict]:
        """
        Gets the color used for the user’s name in chat

        Args:
            user_id (str | list[str]): The ID of the user whose username color you want to get
                Maximum: 100

        Raises:
            twitchpy.errors.ClientError

        Returns:
            list[dict]
        """

        url = "https://api.twitch.tv/helix/chat/color"
        headers = {"Authorization": f"Bearer {self.__app_token}", "Client-Id": self.client_id}
        params = {"user_id": user_id}

        response = requests.get(url, headers=headers, params=params)

        if response.ok:
            return response.json()["data"]

        else:
            raise twitchpy.errors.ClientError(response.json()["message"])

    def update_user_chat_color(self, user_id: str, color: str) -> None:
        """
        Updates the color used for the user’s name in chat

        Args:
            user_id (str): The ID of the user whose chat color you want to update
                This ID must match the user ID in the access token
            color (str): The color to use for the user’s name in chat
                All users may specify one of the following named color values: blue, blue_violet, cadet_blue, chocolate, coral, dodger_blue, firebrick, golden_rod, green, hot_pink, orange_red, red, sea_green, spring_green, yellow_green
                Turbo and Prime users may specify a named color or a Hex color code
        """

        url = "https://api.twitch.tv/helix/chat/color"
        headers = {"Authorization": f"Bearer {self.__user_token}", "Client-Id": self.client_id}
        data = {"user_id": user_id, "color": color}

        requests.put(url, headers=headers, data=data)

    def create_clip(self,broadcaster_id,has_delay=False):
        """
        This returns both an ID and an edit URL for a new clip

        Args:
            broadcaster_id (str): ID of the stream from which the clip will be made
            has_delay (bool, optional): If false, the clip is captured from the live stream when the API is called; otherwise, a delay is added before the clip is captured (to account for the brief delay between the broadcaster’s stream and the viewer’s experience of that stream)
                                        Default: false

        Raises:
            twitchpy.errors.ClientError

        Returns:
            dict
        """

        url="https://api.twitch.tv/helix/clips"
        headers={"Authorization":f"Bearer {self.__user_token}","Client-Id":self.client_id}
        payload={"broadcaster_id":broadcaster_id}

        if has_delay!=False:
            payload["has_delay"]=has_delay

        response=requests.post(url,headers=headers,json=payload)
        
        if response.ok:
            return response.json()["data"]

        else:
            raise twitchpy.errors.ClientError(response.json()["message"])

    def get_clips(self,broadcaster_id="",game_id="",id=[],ended_at="",first=20,started_at=""):
        """
        Gets clip information by clip ID, broadcaster ID or game ID (one only)

        Args:
            broadcaster_id (str, optional): ID of the broadcaster for whom clips are returned
            game_id (str, optional): ID of the game for which clips are returned
            id (list, optional): ID of the clip being queried
                                 Limit: 100
            ended_at (str, optional): Ending date/time for returned clips, in RFC3339 format
                                      If this is specified, started_at also must be specified; otherwise, the time period is ignored
            first (int, optional): Maximum number of objects to return
                                   Default: 20
            started_at (str, optional): Starting date/time for returned clips, in RFC3339 format
                                        If this is specified, ended_at also should be specified; otherwise, the ended_at date/time will be 1 week after the started_at value

        Raises:
            twitchpy.errors.TooManyArgumentsError
            twitchpy.errors.ClientError

        Returns:
            list
        """

        url="https://api.twitch.tv/helix/clips"
        headers={"Authorization":f"Bearer {self.__app_token}","Client-Id":self.client_id}
        params={}

        if broadcaster_id!="":
            params["broadcaster_id"]=broadcaster_id

        if game_id!="":
            params["game_id"]=game_id

        if len(id)>0:
            params["id"]=id

        if ended_at!="":
            params["ended_at"]=ended_at

        if started_at!="":
            params["started_at"]=started_at

        after=""
        calls=math.ceil(first/100)
        clips=[]

        for call in range(calls):
            params["first"] = min(100, first-(100*call))

            if after!="":
                params["after"]=after

            response=requests.get(url,headers=headers,params=params)
            
            if response.ok:
                response=response.json()

                for clip in response["data"]:
                    clips.append(Clip(clip["id"],clip["url"],clip["embed_url"],clip["broadcaster_id"],clip["broadcaster_name"],clip["creator_id"],clip["creator_name"],clip["video_id"],clip["game_id"],clip["language"],clip["title"],clip["view_count"],clip["created_at"],clip["thumbnail_url"],clip["duration"]))

                if "pagination" in response and "cursor" in response["pagination"]:
                    after=response["pagination"]["cursor"]

            else:
                raise twitchpy.errors.ClientError(response.json()["message"])

        return clips

    def get_code_status(self,code,user_id):
        """
        Gets the status of one or more provided codes
        All codes are single-use

        Args:
            code (list): The code to get the status of
                         Maximum: 20
            user_id (int): The user account which is going to receive the entitlement associated with the code

        Raises:
            twitchpy.errors.ClientError

        Returns:
            list
        """

        url="https://api.twitch.tv/helix/entitlements/codes"
        headers={"Authorization":f"Bearer {self.__app_token}","Client-Id":self.client_id}
        params={"code":code,"user_id":user_id}

        response=requests.get(url,headers=headers,params=params)
        
        if response.ok:
            return response.json()["data"]

        else:
            raise twitchpy.errors.ClientError(response.json()["message"])

    def get_drops_entitlements(self,id="",user_id="",game_id="",fulfillment_status="",first=20):
        """
        Gets a list of entitlements for a given organization that have been granted to a game, user, or both

        Args:
            id (str, optional): ID of the entitlement
            user_id (str, optional): A Twitch User ID
            game_id (str, optional): A Twitch Game ID
            fulfillment_status (str, optional): An optional fulfillment status used to filter entitlements
                                                Valid values are "CLAIMED" or "FULFILLED"
            first (int, optional): Maximum number of entitlements to return
                                   Default: 20

        Raises:
            twitchpy.errors.ClientError

        Returns:
            list
        """
        
        url="https://api.twitch.tv/helix/entitlements/drops"
        headers={"Authorization":f"Bearer {self.__app_token}","Client-Id":self.client_id}
        params={}

        if id!="":
            params["id"]=id

        if user_id!="":
            params["user_id"]=user_id

        if game_id!="":
            params["game_id"]=game_id

        if fulfillment_status!="":
            params["fulfillment_status"]=fulfillment_status

        after=""
        calls=math.ceil(first/1000)
        drops_entitlements=[]

        for call in range(calls):
            params["first"] = min(1000, first-(1000*call))

            if after!="":
                params["after"]=after

            response=requests.get(url,headers=headers,params=params)

            if response.ok:
                response=response.json()
                drops_entitlements.extend(response["data"])

                if "pagination" in response:
                    after=response["pagination"]["cursor"]

            else:
                raise twitchpy.errors.ClientError(response.json()["message"])

        return drops_entitlements

    def update_drops_entitlements(self,entitlement_ids=[],fulfillment_status=""):
        """
        Updates the fulfillment status on a set of Drops entitlements, specified by their entitlement IDs

        Args:
            entitlement_ids (list, optional): An array of unique identifiers of the entitlements to update
                                              Maximum: 100
            fulfillment_status (str, optional): A fulfillment status
                                                Valid values are "CLAIMED" or "FULFILLED"

        Raises:
            twitchpy.errors.ClientError

        Returns:
            list
        """

        url="https://api.twitch.tv/helix/entitlements/drops"
        headers = {"Authorization": f"Bearer {self.__app_token}", "Client-Id": self.client_id, "Content-Type": CONTENT_TYPE_APPLICATION_JSON}
        data={}

        if len(entitlement_ids)>0:
            data["entitlement_ids"]=entitlement_ids

        if fulfillment_status!="":
            data["fulfillment_status"]=fulfillment_status

        response=requests.patch(url,headers=headers,data=data)
        
        if response.ok:
            return response.json()["data"]

        else:
            raise twitchpy.errors.ClientError(response.json()["message"])

    def redeem_code(self,code,user_id):
        """
        Redeems one or more provided codes
        All codes are single-use

        Args:
            code (list): The code to redeem to the authenticated user’s account
                         Maximum: 20
            user_id (int): The user account which is going to receive the entitlement associated with the code

        Raises:
            twitchpy.errors.ClientError

        Returns:
            list
        """

        url="https://api.twitch.tv/helix/entitlements/code"
        headers={"Authorization":f"Bearer {self.__app_token}","Client-Id":self.client_id}
        payload={"code":code,"user_id":user_id}

        response=requests.post(url,headers=headers,json=payload)
        
        if response.ok:
            return response.json()["data"]

        else:
            raise twitchpy.errors.ClientError(response.json()["message"])

    def get_extension_configuration_segment(self,broadcaster_id,extension_id,segment):
        """
        Gets the specified configuration segment from the specified extension
        You can retrieve each segment a maximum of 20 times per minute

        Args:
            broadcaster_id (str): The ID of the broadcaster for the configuration returned
                                  This parameter is required if you set the segment parameter to "broadcaster" or "developer"
                                  Do not specify this parameter if you set segment to "global"
            extension_id (str): The ID of the extension that contains the configuration segment you want to get
            segment (list): The type of configuration segment to get
                           Valid values are: "broadcaster", "developer", "global"

        Raises:
            twitchpy.errors.ClientError

        Returns:
            dict
        """

        url="https://api.twitch.tv/helix/extensions/configurations"
        headers={"Authorization":f"Bearer {self.__jwt_token}","Client-Id":self.client_id}
        params={"broadcaster_id":broadcaster_id,"extension_id":extension_id,"segment":segment}

        response=requests.get(url,headers=headers,params=params)

        if response.ok:
            return response.json()["data"][0]

        else:
            raise twitchpy.errors.ClientError(response.json()["message"])

    def set_extension_configuration_segment(self,extension_id,segment,broadcaster_id="",content="",version=""):
        """
        Sets a single configuration segment of any type
        Each segment is limited to 5 KB and can be set at most 20 times per minute
        Updates to this data are not delivered to Extensions that have already been rendered

        Args:
            extension_id (str): ID for the Extension which the configuration is for
            segment (str): Configuration type
                           Valid values are "global", "developer", or "broadcaster"
            broadcaster_id (str, optional): User ID of the broadcaster
                                            Required if the segment type is "developer" or "broadcaster"
            content (str, optional): Configuration in a string-encoded format
            version (str, optional): Configuration version with the segment type
        """

        url="https://api.twitch.tv/helix/extensions/configurations"
        headers={"Authorization":f"Bearer {self.__jwt_token}","Client-Id":self.client_id}
        data={"extension_id":extension_id,"segment":segment}

        if broadcaster_id!="":
            data["broadcaster_id"]=broadcaster_id

        if content!="":
            data["content"]=content

        if version!="":
            data["version"]=version

        requests.put(url,headers=headers,data=data)

    def set_extension_required_configuration(self,broadcaster_id,extension_id,extension_version,configuration_version):
        """
        Enable activation of a specified Extension, after any required broadcaster configuration is correct

        Args:
            broadcaster_id (str): User ID of the broadcaster who has activated the specified Extension on their channel
            extension_id (str): ID for the Extension to activate
            extension_version (str): The version fo the Extension to release
            configuration_version (str): The version of the configuration to use with the Extension
        """

        url="https://api.twitch.tv/helix/extensions/required_configuration"
        headers={"Authorization":f"Bearer {self.__jwt_token}","Client-Id":self.client_id}
        data={"broadcaster_id":broadcaster_id,"extension_id":extension_id,"extension_version":extension_version,"configuration_version":configuration_version}

        requests.put(url,headers=headers,data=data)

    def send_extension_pubsub_message(self,target,broadcaster_id,is_global_broadcast,message):
        """
        A message can be sent to either a specified channel or globally (all channels on which your extension is active)
        Extension PubSub has a rate limit of 100 requests per minute for a combination of Extension client ID and broadcaster ID

        Args:
            target (list): Array of strings for valid PubSub targets
                           Valid values: "broadcast", "global", "whisper-<user-id>"
            broadcaster_id (str): ID of the broadcaster receiving the payload
            is_global_broadcast (bool): Indicates if the message should be sent to all channels where your Extension is active
            message (str): String-encoded JSON message to be sent
        """

        url="https://api.twitch.tv/helix/extensions/pubsub"
        headers={"Authorization":f"Bearer {self.__jwt_token}","Client-Id":self.client_id}
        data={"target":target,"broadcaster_id":broadcaster_id,"is_global_broadcast":is_global_broadcast,"message":message}

        requests.post(url,headers=headers,data=data)

    def get_extension_live_channels(self,extension_id,first=20):
        """
        Returns one page of live channels that have installed or activated a specific Extension, identified by a client ID value assigned to the Extension when it is created
        A channel that recently went live may take a few minutes to appear in this list, and a channel may continue to appear on this list for a few minutes after it stops broadcasting

        Args:
            extension_id (str): ID of the Extension to search for
            first (int, optional): Maximum number of objects to return
                                   Default: 20

        Raises:
            twitchpy.errors.ClientError

        Returns:
            list
        """

        url="https://api.twitch.tv/helix/extensions/live"
        headers={"Authorization":f"Bearer {self.__app_token}","Client-Id":{self.client_id}}
        params={"extension_id":extension_id}

        after=""
        calls=math.ceil(first/100)
        channels=[]

        for call in range(calls):
            params["first"] = min(100, first-(100*call))

            if after!="":
                params["after"]=after

            response=requests.get(url,headers=headers,params=params)
            
            if response.ok:
                response=response.json()

                for channel in response["data"]:
                    channels.append(channel)

                if "pagination" in response:
                    after=response["pagination"]["cursor"]

            else:
                raise twitchpy.errors.ClientError(response.json()["message"])

        return channels

    def get_extension_secrets(self):
        """
        Retrieves a specified Extension’s secret data consisting of a version and an array of secret objects
        Each secret object contains a base64-encoded secret, a UTC timestamp when the secret becomes active, and a timestamp when the secret expires

        Raises:
            twitchpy.errors.ClientError

        Returns:
            list
        """

        url="https://api.twitch.tv/helix/extensions/jwt/secrets"
        headers={"Authorization":f"Bearer {self.__jwt_token}","Client-Id":self.client_id}
        
        response=requests.get(url,headers=headers)

        if response.ok:
            return response.json()["data"]

        else:
            raise twitchpy.errors.ClientError(response.json()["message"])

    def create_extension_secret(self,delay=300):
        """
        Creates a JWT signing secret for a specific Extension
        Also rotates any current secrets out of service, with enough time for instances of the Extension to gracefully switch over to the new secret

        Args:
            delay (int, optional): JWT signing activation delay for the newly created secret in seconds
                                   Minimum: 300
                                   Default: 300

        Raises:
            twitchpy.errors.ClientError

        Returns:
            list
        """

        url="https://api.twitch.tv/helix/extensions/jwt/secrets"
        headers={"Authorization":f"Bearer {self.__jwt_token}","Client-Id":self.client_id}
        payload={}

        if delay!=300:
            payload["delay"]=delay

        response=requests.post(url,headers=headers,json=payload)

        if response.ok:
            return response.json()["data"][0]

        else:
            raise twitchpy.errors.ClientError(response.json()["message"])

    def send_extension_chat_message(self,broadcaster_id,text,extension_id,extension_version):
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
        """

        url="https://api.twitch.tv/helix/extensions/chat"
        headers={"Authorization":f"Bearer {self.__jwt_token}","Client-Id":self.client_id}
        payload={"broadcaster_id":broadcaster_id,"text":text,"extension_id":extension_id,"extension_version":extension_version}

        requests.post(url,headers=headers,json=payload)

    def get_extensions(self,extension_id,extension_version=""):
        """
        Gets information about your Extensions; either the current version or a specified version

        Args:
            extension_id (str): ID of the Extension
            extension_version (str, optional): The specific version of the Extension to return
                                               If not provided, the current version is returned

        Raises:
            twitchpy.errors.ClientError

        Returns:
            list
        """

        url="https://api.twitch.tv/helix/extensions"
        headers={"Authorization":f"Bearer {self.__jwt_token}","Client-Id":self.client_id}
        params={"extension_id":extension_id}

        if extension_version!="":
            params["extension_version"]=extension_version

        response=requests.get(url,headers=headers,params=params)

        if response.ok:
            extensions=[]

            for extension in response.json()["data"]:
                extensions.append(Extension(extension["author_name"],extension["bits_enables"],extension["can_install"],extension["configuration_location"],extension["description"],extension["eula_tos_url"],extension["has_chat_support"],extension["icon_url"],extension["icon_urls"],extension["id"],extension["name"],extension["privacy_policy_url"],extension["request_identity_link"],extension["screenshot_urls"],extension["state"],extension["subscriptions_support_level"],extension["summary"],extension["support_email"],extension["version"],extension["viewer_summary"],extension["views"],extension["allowlisted_config_urls"],extension["allowlisted_panel_urls"]))

            return extensions

        else:
            raise twitchpy.errors.ClientError(response.json()["message"])

    def get_released_extensions(self,extension_id,extension_version=""):
        """
        Gets information about a released Extension; either the current version or a specified version

        Args:
            extension_id (str): ID of the Extension
            extension_version (str, optional): The specific version of the Extension to return
                                               If not provided, the current version is returned

        Raises:
            twitchpy.errors.ClientError

        Returns:
            list
        """

        url="https://api.twitch.tv/helix/extensions/released"
        headers={"Authorization":f"Bearer {self.__app_token}","Client-Id":self.client_id}
        params={"extension_id":extension_id}

        if extension_version!="":
            params["extension_version"]=extension_version

        response=requests.get(url,headers=headers,params=params)

        if response.ok:
            extensions=[]

            for extension in response.json()["data"]:
                extensions.append(Extension(extension["author_name"],extension["bits_enables"],extension["can_install"],extension["configuration_location"],extension["description"],extension["eula_tos_url"],extension["has_chat_support"],extension["icon_url"],extension["icon_urls"],extension["id"],extension["name"],extension["privacy_policy_url"],extension["request_identity_link"],extension["screenshot_urls"],extension["state"],extension["subscriptions_support_level"],extension["summary"],extension["support_email"],extension["version"],extension["viewer_summary"],extension["views"],extension["allowlisted_config_urls"],extension["allowlisted_panel_urls"]))

            return extensions

        else:
            raise twitchpy.errors.ClientError(response.json()["message"])

    def get_extension_bits_products(self,extension_client_id,should_include_all=False):
        """
        Gets a list of Bits products that belongs to an Extension

        Args:
            extension_client_id (str): Extension client ID
            should_include_all (bool, optional): Whether Bits products that are disabled/expired should be included in the response
                                                 Default: false

        Raises:
            twitchpy.errors.ClientError

        Returns:
            list
        """

        url="https://api.twitch.tv/helix/bits/extensions"
        headers={"Authorization":f"Bearer {self.__app_token}","Client-Id":extension_client_id}
        params={}

        if should_include_all!=False:
            params["should_include_all"]=should_include_all

        response=requests.get(url,headers=headers,params=params)

        if response.ok:
            return response.json()["data"]

        else:
            raise twitchpy.errors.ClientError(response.json()["message"])

    def update_extension_bits_product(self,extension_client_id,sku,cost,display_name,in_development=False,expiration="",is_broadcast=False):
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
            in_development (bool, optional): Set to true if the product is in development and not yet released for public use
                                             Default: false
            expiration (str, optional): Expiration time for the product in RFC3339 format
                                        If not provided, the Bits product will not have an expiration date
                                        Setting an expiration in the past will disable the product
            is_broadcast (bool, optional): Indicates if Bits product purchase events are broadcast to all instances of an Extension on a channel via the “onTransactionComplete” helper callback
                                           Default: false

        Raises:
            twitchpy.errors.ClientError

        Returns:
            dict
        """

        url="https://api.twitch.tv/helix/bits/extensions"
        headers={"Authorization":f"Bearer {self.__app_token}","Client-Id":extension_client_id}
        data={"sku":sku,"cost":cost,"display_name":display_name}

        if in_development!=False:
            data["in_development"]=in_development

        if expiration!="":
            data["expiration"]=expiration

        if is_broadcast!=False:
            data["is_broadcast"]=is_broadcast

        response=requests.put(url,headers=headers,data=data)

        if response.ok:
            return response.json()["data"][0]

        else:
            raise twitchpy.errors.ClientError(response.json()["message"])

    def create_eventsub_subscription(self,type,version,condition,transport):
        """
        Creates an EventSub subscription

        Args:
            type (str): The category of the subscription that is being created
                        Valid values: "channel.update", "channel.follow", "channel.subscribe", "channel.subscription.end", "channel.subscription.gift","channel.subscription.message", "channel.cheer", "channel.raid", "channel.ban", "channel.unban", "channel.moderator.add", "channel.moderator.remove", "channel.channel_points_custom_reward.add", "channel.channel_points_custom_reward.update", "channel.channel_points_custom_reward.remove", "channel.channel_points_custom_reward_redemption.add", "channel.channel_points_custom_reward_redemption.update", "channel.poll.begin", "channel.poll.progress", "channel.poll.end", "channel.prediction.begin", "channel.prediction.progress", "channel.prediction.lock", "channel.prediction.end", "drop.entitlement.grant", "extension.bits_transaction.create", "channel.hype_train.begin", "channel.hype_train.progress", "channel.hype_train.end", "stream.online", "stream.offline", "user.authorization.grant", "user.authorization.revoke", "user.update"
            version (str): The version of the subscription type that is being created
                           Each subscription type has independent versioning
            condition (dict): Custom parameters for the subscription
            transport (dict): Notification delivery specific configuration including a method string
                              Valid transport methods include: webhook
                              In addition to the method string, a webhook transport must include the callback and secret information

        Raises:
            twitchpy.errors.ClientError

        Returns:
            EventSubSubscription
        """

        url = ENDPOINT_EVENTSUB_SUBSCRIPTION
        headers = {"Authorization": f"Bearer {self.__app_token}", "Client-Id": self.client_id, "Content-Type": CONTENT_TYPE_APPLICATION_JSON}
        payload={"type":type,"version":version,"condition":condition,"transport":transport}

        response=requests.post(url,headers=headers,json=payload)
        
        if response.ok:
            subscription=response.json()["data"][0]
            subscription=EventSubSubscription(subscription["id"],subscription["status"],subscription["type"],subscription["version"],subscription["condition"],subscription["created_at"],subscription["transport"],subscription["cost"])

            return subscription

        else:
            raise twitchpy.errors.ClientError(response.json()["message"])

    def delete_eventsub_subscription(self,id):
        """
        Delete an EventSub subscription

        Args:
            id (str): The subscription ID for the subscription to delete
        """

        url = ENDPOINT_EVENTSUB_SUBSCRIPTION
        headers={"Authorization":f"Bearer {self.__app_token}","Client-Id":self.client_id}
        data={"id":id}

        requests.delete(url,headers=headers,data=data)

    def get_eventsub_subscriptions(self, status: str = "", type: str = "", user_id: str = "") -> list[EventSubSubscription]:
        """
        Get a list of your EventSub subscriptions
        Only include one filter query parameter

        Args:
            status (str, optional): Filters subscriptions by one status type
                Valid values: "enabled", "webhook_callback_verification_pending", "webhook_callback_verification_failed", "notification_failures_exceeded", "authorization_revoked", "user_removed"
            type (str, optional): Filters subscriptions by subscription type name
            user_id (str, optional): Filter subscriptions by user ID

        Raises:
            twitchpy.errors.ClientError

        Returns:
            list[EventSubSubscription]
        """
        
        url = ENDPOINT_EVENTSUB_SUBSCRIPTION
        headers={"Authorization":f"Bearer {self.__app_token}","Client-Id":self.client_id}
        params={}

        if status!="":
            params["status"]=status

        if type!="":
            params["type"]=type

        if user_id != "":
            params["user_id"] = user_id

        response=requests.get(url,headers=headers,params=params)
        
        if response.ok:
            subscriptions=[]

            for subscription in response.json()["data"]:
                subscriptions.append(EventSubSubscription(subscription["id"],subscription["status"],subscription["type"],subscription["version"],subscription["condition"],subscription["created_at"],subscription["transport"],subscription["cost"]))

            return subscriptions

        else:
            raise twitchpy.errors.ClientError(response.json()["message"])

    def get_top_games(self,first=20):
        """
        Gets games sorted by number of current viewers on Twitch, most popular first

        Args:
            first (int, optional): Maximum number of objects to return
                                   Default: 20

        Raises:
            twitchpy.errors.ClientError

        Returns:
            list
        """

        url=f"https://api.twitch.tv/helix/games/top"
        headers={"Authorization": f"Bearer {self.__app_token}","Client-Id":self.client_id}
        params={}

        after=""
        calls=math.ceil(first/100)
        games=[]

        for call in range(calls):
            params["first"] = min(100, first-(100*call))

            if after!="":
                params["after"]=after

            response=requests.get(url,headers=headers,params=params)
            
            if response.ok:
                response=response.json()

                for game in response["data"]:
                    games.append(Game(game["id"], game["name"], game["box_art_url"], game["igdb_id"]))

                if "pagination" in response:
                    after=response["pagination"]["cursor"]

            else:
                raise twitchpy.errors.ClientError(response.json()["message"])

        return games

    def get_games(self, id: list[str] = [], name: list[str] = [], igdb_id: list[str] = []) -> list[Game]:
        """
        Gets information about specified categories or games

        Args:
            id (list[str]): The ID of the category or game to get
                Maximum: 100
            name (list[str]): The name of the category or game to get
                Maximum: 100
            igdb_id (list[str]): The IGDB ID of the game to get
                Maximum: 100

        Raises:
            twitchpy.errors.ClientError

        Returns:
            list[Game]
        """

        url = "https://api.twitch.tv/helix/games"
        headers = {"Authorization": f"Bearer {self.__app_token}", "Client-Id": self.client_id}
        params = {}

        if len(id) > 0:
            params["id"] = id

        if len(name) > 0:
            params["name"] = name

        if len(igdb_id) > 0:
            params["igdb_id"] = igdb_id

        response = requests.get(url, headers=headers, params=params)

        if response.ok:
            games = []

            for game in response.json()["data"]:
                games.append(Game(game["id"], game["name"], game["box_art_url"], game["igdb_id"]))

        else:
            raise twitchpy.errors.ClientError(response.json()["message"])

        return games

    def get_creator_goals(self,broadcaster_id):
        """
        Gets the broadcaster’s list of active goals
        Use this to get the current progress of each goal

        Args:
            broadcaster_id (str): The ID of the broadcaster that created the goals

        Raises:
            twitchpy.errors.ClientError

        Returns:
            list
        """
        
        url="https://api.twitch.tv/helix/goals"
        headers={"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id}
        params={"broadcaster_id":broadcaster_id}

        response=requests.get(url,headers=headers,params=params)
        
        if response.ok:
            return response.json()["data"]

        else:
            raise twitchpy.errors.ClientError(response.json()["message"])

    def get_hype_train_events(self, broadcaster_id: str, first: int=1) -> list[HypeTrainEvent]:
        """
        Gets the information of the most recent Hype Train of the given channel ID
        When there is currently an active Hype Train, it returns information about that Hype Train
        When there is currently no active Hype Train, it returns information about the most recent Hype Train
        After 5 days, if no Hype Train has been active, the endpoint will return an empty response

        Args:
            broadcaster_id (str): User ID of the broadcaster
                Must match the User ID in the Bearer token if User Token is used
            first (int, optional): Maximum number of objects to return
                Default: 1

        Raises:
            twitchpy.errors.ClientError

        Returns:
            list[HypeTrainEvent]
        """

        url="https://api.twitch.tv/helix/hypetrain/events"
        headers={"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id}
        params={"broadcaster_id":broadcaster_id}
        
        cursor=""
        calls=math.ceil(first/100)
        events=[]

        for call in range(calls):
            params["first"] = min(100, first-(100*call))

            if cursor!="":
                params["cursor"]=cursor

            response=requests.get(url,headers=headers,params=params)
            
            if response.ok:
                response=response.json()

                for event in response["data"]:
                    events.append(HypeTrainEvent(event["id"],event["event_type"],event["event_timestamp"],event["version"],event["event_data"]))

                if "pagination" in response and response["pagination"]!=None:
                    cursor=response["pagination"]["cursor"]

            else:
                raise twitchpy.errors.ClientError(response.json()["message"])

        return events

    def check_automod_status(self, broadcaster_id: str, msg_id: str, msg_user: str) -> list[dict]:
        """
        Determines whether a string message meets the channel’s AutoMod requirements

        Args:
            broadcaster_id (str): Provided broadcaster_id must match the user_id in the auth token
            msg_id (str): Developer-generated identifier for mapping messages to results
            msg_user (str): Message text

        Raises:
            twitchpy.errors.ClientError

        Returns:
            list[dict]
        """

        url = "https://api.twitch.tv/helix/moderation/enforcements/status"
        headers = {"Authorization": f"Bearer {self.__user_token}", "Client-Id": self.client_id}
        payload = {"broadcaster_id": broadcaster_id, "data": [{"msg_id": msg_id, "msg_user": msg_user}]}

        response = requests.post(url, headers = headers, json = payload)
        
        if response.ok:
            return response.json()["data"]

        else:
            raise twitchpy.errors.ClientError(response.json()["message"])

    def manage_held_automod_messages(self,user_id,msg_id,action):
        """
        Allow or deny a message that was held for review by AutoMod

        Args:
            user_id (str): The moderator who is approving or rejecting the held message
                           Must match the user_id in the user OAuth token
            msg_id (str): ID of the message to be allowed or denied
            action (str): The action to take for the message
                          Must be "ALLOW" or "DENY"
        """

        url="https://api.twitch.tv/helix/moderation/automod/message"
        headers={"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id}
        payload={"user_id":user_id,"msg_id":msg_id,"action":action}

        requests.post(url,headers=headers,json=payload)

    def get_automod_settings(self,broadcaster_id,moderator_id):
        """
        Gets the broadcaster’s AutoMod settings, which are used to automatically block inappropriate or harassing messages from appearing in the broadcaster’s chat room

        Args:
            broadcaster_id (str): The ID of the broadcaster whose AutoMod settings you want to get
            moderator_id (str): The ID of a user that has permission to moderate the broadcaster’s chat room
                                This ID must match the user ID associated with the user OAuth token
                                If the broadcaster wants to get their own AutoMod settings (instead of having the moderator do it), set this parameter to the broadcaster’s ID, too

        Raises:
            twitchpy.errors.ClientError

        Returns:
            dict
        """

        url="https://api.twitch.tv/helix/moderation/automod/settings"
        headers={"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id}
        params={"broadcaster_id":broadcaster_id,"moderator_id":moderator_id}

        response=requests.get(url,headers=headers,params=params)

        if response.ok:
            return response.json()["data"][0]

        else:
            raise twitchpy.errors.ClientError(response.json()["message"])

    def update_automod_settings(self,broadcaster_id,moderator_id,aggression=None,bullying=None,disability=None,misogyny=None,overall_level=None,race_ethnicity_or_religion=None,sex_based_terms=None,sexuality_sex_or_gender=None,swearing=None):
        """
        Updates the broadcaster’s AutoMod settings, which are used to automatically block inappropriate or harassing messages from appearing in the broadcaster’s chat room

        Args:
            broadcaster_id (str): The ID of the broadcaster whose AutoMod settings you want to update
            moderator_id (str): The ID of a user that has permission to moderate the broadcaster’s chat room
                                This ID must match the user ID associated with the user OAuth token
                                If the broadcaster wants to update their own AutoMod settings (instead of having the moderator do it), set this parameter to the broadcaster’s ID, too
            aggression (int, optional): The Automod level for hostility involving aggression
            bullying (int, optional): The Automod level for hostility involving name calling or insults
            disability (int, optional): The Automod level for discrimination against disability
            misogyny (int, optional): The Automod level for discrimination against women
            overall_level (int, optional): The default AutoMod level for the broadcaster
            race_ethnicity_or_religion (int, optional): The Automod level for racial discrimination
            sex_based_terms (int, optional): The Automod level for sexual content
            sexuality_sex_or_gender (int, optional): The AutoMod level for discrimination based on sexuality, sex, or gender
            swearing (int, optional): The Automod level for profanity

        Raises:
            twitchpy.errors.ClientError

        Returns:
            dict
        """
        
        url="https://api.twitch.tv/helix/moderation/automod/settings"
        headers = {"Authorization": f"Bearer {self.__user_token}", "Client-Id": self.client_id, "Content-Type": CONTENT_TYPE_APPLICATION_JSON}
        data={"broadcaster_id":broadcaster_id,"moderator_id":moderator_id}

        if aggression!=None:
            data["aggression"]=aggression

        if bullying!=None:
            data["bullying"]=bullying

        if disability!=None:
            data["disability"]=disability
        
        if misogyny!=None:
            data["misogyny"]=misogyny
        
        if overall_level!=None:
            data["overall_level"]=overall_level

        if race_ethnicity_or_religion!=None:
            data["race_ethnicity_or_religion"]=race_ethnicity_or_religion

        if sex_based_terms!=None:
            data["sex_based_terms"]=sex_based_terms

        if sexuality_sex_or_gender!=None:
            data["sexuality_sex_or_gender"]=sexuality_sex_or_gender

        if swearing!=None:
            data["swearing"]=swearing

        response=requests.put(url,headers=headers,json=data)

        if response.ok:
            return response.json()["data"][0]

        else:
            raise twitchpy.errors.ClientError(response.json()["message"])

    def get_banned_users(self,broadcaster_id,user_id=[],first=20):
        """
        Returns all banned and timed-out users in a channel

        Args:
            broadcaster_id (str): Provided broadcaster_id must match the user_id in the auth token
            user_id (list, optional): Filters the results and only returns a status object for users who are banned in this channel and have a matching user_id
                                     Maximum: 100
            first (int, optional): Maximum number of objects to return
                                   Default: 20

        Raises:
            twitchpy.errors.ClientError

        Returns:
            list
        """

        url="https://api.twitch.tv/helix/moderation/banned"
        headers={"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id}
        params={"broadcaster_id":broadcaster_id}

        if len(user_id)>0:
            params["user_id"]=user_id

        if first!=20:
            params["first"]=first

        after=""
        calls=math.ceil(first/100)
        users=[]

        for call in range(calls):
            if first-(100*call)>100:
                params["first"]=100
            
            else:
                params["first"]=first-(100*call)

            if after!="":
                params["after"]=after

            response=requests.get(url,headers=headers,params=params)
            
            if response.ok:
                response=response.json()
                users.extend(response["data"])

                if "pagination" in response and "cursor" in response["pagination"]:
                    after=response["pagination"]["cursor"]

            else:
                raise twitchpy.errors.ClientError(response.json()["message"])

        return users

    def ban_user(self,broadcaster_id,moderator_id,reason,user_id,duration=None):
        """
        Bans a user from participating in a broadcaster’s chat room, or puts them in a timeout
        If the user is currently in a timeout, you can use this method to change the duration of the timeout or ban them altogether
        If the user is currently banned, you cannot call this method to put them in a timeout instead

        Args:
            broadcaster_id (str): The ID of the broadcaster whose chat room the user is being banned from
            moderator_id (str): The ID of a user that has permission to moderate the broadcaster’s chat room
                                This ID must match the user ID associated with the user OAuth token
                                If the broadcaster wants to ban the user (instead of having the moderator do it), set this parameter to the broadcaster’s ID, too
            reason (reason): The reason the user is being banned or put in a timeout
                             The text is user defined and limited to a maximum of 500 characters
            user_id (str): The ID of the user to ban or put in a timeout
            duration (int, optional): To ban a user indefinitely, don’t include this field
                                      To put a user in a timeout, include this field and specify the timeout period, in seconds
                                      The minimum timeout is 1 second and the maximum is 1,209,600 seconds (2 weeks)
                                      To end a user’s timeout early, set this field to 1

        Raises:
            twitchpy.errors.ClientError

        Returns:
            dict
        """

        url="https://api.twitch.tv/helix/moderation/bans"
        headers={"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id}
        payload={"broadcaster_id":broadcaster_id,"moderator_id":moderator_id}

        data={"reason":reason,"user_id":user_id}

        if duration!=None:
            data["duration"]=duration

        payload["data"]=data
        
        response=requests.post(url,headers=headers,json=payload)

        if response.ok:
            return response.json()["data"]
        
        else:
            raise twitchpy.errors.ClientError(response.json()["message"])

    def unban_user(self,broadcaster_id,moderator_id,user_id):
        """
        Removes the ban or timeout that was placed on the specified user

        Args:
            broadcaster_id (str): The ID of the broadcaster whose chat room the user is banned from chatting in
            moderator_id (str): The ID of a user that has permission to moderate the broadcaster’s chat room
                                This ID must match the user ID associated with the user OAuth token
                                If the broadcaster wants to remove the ban (instead of having the moderator do it), set this parameter to the broadcaster’s ID, too
            user_id (str): The ID of the user to remove the ban or timeout from

        Raises:
            twitchpy.errors.ClientError
        """

        url="https://api.twitch.tv/helix/moderation/bans"
        headers={"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id}
        data={"broadcaster_id":broadcaster_id,"moderator_id":moderator_id,"user_id":user_id}

        requests.delete(url,headers=headers,data=data)

    def get_blocked_terms(self,broadcaster_id,moderator_id,first=20):
        """
        Gets the broadcaster’s list of non-private, blocked words or phrases
        These are the terms that the broadcaster or moderator added manually, or that were denied by AutoMod

        Args:
            broadcaster_id (str): The ID of the broadcaster whose blocked terms you’re getting
            moderator_id (str): The ID of a user that has permission to moderate the broadcaster’s chat room
                                This ID must match the user ID associated with the user OAuth token
                                If the broadcaster wants to get their own block terms (instead of having the moderator do it), set this parameter to the broadcaster’s ID, too
            first (int, optional): The maximum number of blocked terms to return per page in the response
                                   The minimum page size is 1 blocked term per page and the maximum is 100
                                   The default is 20

        Raises:
            twitchpy.errors.ClientError

        Returns:
            list
        """
        
        url = ENDPOINT_MODERATION_BLOCKED_TERMS
        headers={"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id}
        params={"broadcaster_id":broadcaster_id,"moderator_id":moderator_id}

        if first!=20:
            params["first"]=first
        
        after=""
        calls=math.ceil(first/100)
        blocked_terms=[]

        for call in range(calls):
            if first-(100*call)>100:
                params["first"]=100
            
            else:
                params["first"]=first-(100*call)

            if after!="":
                params["after"]=after

            response=requests.get(url,headers=headers,params=params)
            
            if response.ok:
                response=response.json()
                blocked_terms.extend(response["data"])

                if "pagination" in response and "cursor" in response["pagination"]:
                    after=response["pagination"]["cursor"]

            else:
                raise twitchpy.errors.ClientError(response.json()["message"])
        
        return blocked_terms

    def add_blocked_term(self,broadcaster_id,moderator_id,text):
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
            twitchpy.errors.ClientError

        Returns:
            dict
        """

        url = ENDPOINT_MODERATION_BLOCKED_TERMS
        headers = {"Authorization": f"Bearer {self.__user_token}", "Client-Id": self.client_id, "Content-Type": CONTENT_TYPE_APPLICATION_JSON}
        payload={"broadcaster_id":broadcaster_id,"moderator_id":moderator_id,"text":text}

        response=requests.post(url,headers=headers,json=payload)

        if response.ok:
            return response.json()["data"][0]

        else:
            raise twitchpy.errors.ClientError(response.json()["message"])

    def remove_blocked_term(self,broadcaster_id,id,moderator_id):
        """
        Removes the word or phrase that the broadcaster is blocking users from using in their chat room

        Args:
            broadcaster_id (str): The ID of the broadcaster that owns the list of blocked terms
            id (str): The ID of the blocked term you want to delete
            moderator_id (str): The ID of a user that has permission to moderate the broadcaster’s chat room
                                This ID must match the user ID associated with the user OAuth token
                                If the broadcaster wants to delete the blocked term (instead of having the moderator do it), set this parameter to the broadcaster’s ID, too
        """

        url = ENDPOINT_MODERATION_BLOCKED_TERMS
        headers={"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id}
        data={"broadcaster_id":broadcaster_id,"id":id,"moderator_id":moderator_id}

        requests.delete(url,headers=headers,data=data)

    def delete_chat_messages(self, broadcaster_id: str, moderator_id: str, message_id: str = "") -> None:
        """
        Removes a single chat message or all chat messages from the broadcaster’s chat room

        Args:
            broadcaster_id (str): The ID of the broadcaster that owns the chat room to remove messages from
            moderator_id (str): The ID of the broadcaster or a user that has permission to moderate the broadcaster’s chat room
                This ID must match the user ID in the user access token
            message_id (str, optional): The ID of the message to remove
                If not specified, the request removes all messages in the broadcaster’s chat room
        """

        url = "https://api.twitch.tv/helix/moderation/chat"
        headers = {"Authorization": f"Bearer {self.__user_token}", "Client-Id": self.client_id}
        data = {"broadcaster_id": broadcaster_id, "moderator_id": moderator_id}

        if message_id != "":
            data["message_id"] = message_id

        requests.delete(url, headers=headers, data=data)

    def get_moderators(self,broadcaster_id,user_id=[],first=20):
        """
        Returns all moderators in a channel

        Args:
            broadcaster_id (str): Provided broadcaster_id must match the user_id in the auth token
            user_id (list, optional): Filters the results and only returns a status object for users who are moderators in this channel and have a matching user_id
                                      Maximum: 100
            first (int, optional): Maximum number of objects to return
                                   Default: 20

        Raises:
            twitchpy.errors.ClientError

        Returns:
            list
        """

        url="https://api.twitch.tv/helix/moderation/moderators"
        headers={"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id}
        params={"broadcaster_id":broadcaster_id}

        if len(user_id)>0:
            params["user_id"]=user_id

        after=""
        calls=math.ceil(first/100)
        ids=[]

        for call in range(calls):
            params["first"] = min(100, first-(100*call))

            if after!="":
                params["after"]=after

            response=requests.get(url,headers=headers,params=params)
            
            if response.ok:
                response=response.json()
                
                for user in response["data"]:
                    ids.append(user["user_id"])

                if "pagination" in response and "cursor" in response["pagination"]:
                    after=response["pagination"]["cursor"]

            else:
                raise twitchpy.errors.ClientError(response.json()["message"])

        return self.get_users(id=ids)

    def add_channel_moderator(self, broadcaster_id: str, user_id: str) -> None:
        """
        Adds a moderator to the broadcaster’s chat room

        Args:
            broadcaster_id (str): The ID of the broadcaster that owns the chat room
                This ID must match the user ID in the access token
            user_id (str): The ID of the user to add as a moderator in the broadcaster’s chat room
        """

        url = "https://api.twitch.tv/helix/moderation/moderators"
        headers = {"Authorization": f"Bearer {self.__user_token}", "Client-Id": self.client_id}
        payload = {"broadcaster_id": broadcaster_id, "user_id": user_id}

        requests.post(url, headers=headers, json=payload)

    def remove_channel_moderator(self, broadcaster_id: str, user_id: str) -> None:
        """
        Removes a moderator from the broadcaster’s chat room

        Args:
            broadcaster_id (str): The ID of the broadcaster that owns the chat room
                This ID must match the user ID in the access token
            user_id (str): The ID of the user to remove as a moderator from the broadcaster’s chat room
        """

        url = "https://api.twitch.tv/helix/moderation/moderators"
        headers = {"Authorization": f"Bearer {self.__user_token}", "Client-Id": self.client_id}
        data = {"broadcaster_id": broadcaster_id, "user_id": user_id}

        requests.delete(url, headers=headers, data=data)

    def get_vips(self, broadcaster_id: str, user_id: list[str] = [], first: int = 20) -> list[User]:
        """
        Gets a list of the broadcaster’s VIPs

        Args:
            broadcaster_id (str): The ID of the broadcaster whose list of VIPs you want to get
                This ID must match the user ID in the access token
            user_id (list[str]): Filters the list for specific VIPs
                Maximum: 100
            first (int): The number of items to return
                Minimum: 1
                Maximum: 100

        Raises:
            twitchpy.errors.ClientError

        Returns:
            list[User]
        """

        url = ENDPOINT_VIPS
        headers = {"Authorization": f"Bearer {self.__user_token}", "Client-Id": self.client_id}
        params = {"broadcaster_id": broadcaster_id}

        if len(user_id) > 0:
            params["user_id"] = user_id

        after = ""
        calls = math.ceil(first / 20)
        users = []

        for call in range(calls):
            params["first"] = min(20, first - (20 * call))

            if after != "":
                params["after"] = after

            response = requests.get(url, headers=headers, params=params)

            if response.ok:
                response = response.json()

                if response["data"] is not None:
                    users.append(self.get_users(id=[user["user_id"] for user in response["data"]]))

                if "pagination" in response and "cursor" in response["pagination"]:
                    after = response["pagination"]["cursor"]

            else:
                raise twitchpy.errors.ClientError(response.json()["message"])

        return users

    def add_channel_vip(self, user_id: str, broadcaster_id: str) -> None:
        """
        Adds the specified user as a VIP in the broadcaster’s channel

        Args:
            user_id (str): The ID of the user to give VIP status to
            broadcaster_id (str): The ID of the broadcaster that’s adding the user as a VIP
                This ID must match the user ID in the access token
        """

        url = ENDPOINT_VIPS
        headers = {"Authorization": f"Bearer {self.__user_token}", "Client-Id": self.client_id}
        payload = {"user_id": user_id, "broadcaster_id": broadcaster_id}

        requests.post(url, headers=headers, json=payload)

    def remove_channel_vip(self, user_id: str, broadcaster_id: str) -> None:
        """
        Removes the specified user as a VIP in the broadcaster’s channel

        Args:
            user_id (str): The ID of the user to remove VIP status from
            broadcaster_id (str): The ID of the user to remove VIP status from
        """

        url = ENDPOINT_VIPS
        headers = {"Authorization": f"Bearer {self.__user_token}", "Client-Id": self.client_id}
        data = {"user_id": user_id, "broadcaster_id": broadcaster_id}

        requests.delete(url, headers=headers, data=data)

    def get_polls(self,broadcaster_id,id=[],first=20):
        """
        Get information about all polls or specific polls for a Twitch channel
        Poll information is available for 90 days

        Args:
            broadcaster_id (str): The broadcaster running polls
                                  Provided broadcaster_id must match the user_id in the user OAuth token
            id (list, optional): ID of a poll
                                 Maximum: 100
            first (int, optional): Maximum number of objects to return
                                   Default: 20

        Raises:
            twitchpy.errors.ClientError

        Returns:
            list
        """

        url = ENDPOINT_POLLS
        headers={"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id}
        params={"broadcaster_id":broadcaster_id}

        if len(id)>0:
            params["id"]=id

        after=""
        calls=math.ceil(first/20)
        polls=[]

        for call in range(calls):
            params["first"] = min(20, first-(20*call))

            if after!="":
                params["after"]=after

            response=requests.get(url,headers=headers,params=params)

            if response.ok:
                response=response.json()
                
                if response["data"]!=None:
                    for poll in response["data"]:
                        polls.append(Poll(poll["id"],poll["broadcaster_id"],poll["broadcaster_name"],poll["broadcaster_login"],poll["title"],poll["choices"],poll["bits_voting_enabled"],poll["bits_per_vote"],poll["channel_points_voting_enabled"],poll["channel_points_per_vote"],poll["status"],poll["duration"],poll["started_at"]))

                if "pagination" in response and "cursor" in response["pagination"]:
                    after=response["pagination"]["cursor"]

            else:
                raise twitchpy.errors.ClientError(response.json()["message"])

        return polls

    def create_poll(self, broadcaster_id: str, title: str, choices: list[str], duration: int, channel_points_voting_enabled: bool=False, channel_points_per_vote: int=0) -> Poll:
        """
        Create a poll for a specific Twitch channel

        Args:
            broadcaster_id (str): The broadcaster running polls
                Provided broadcaster_id must match the user_id in the user OAuth token
            title (str): Question displayed for the poll
                Maximum: 60 characters
            choices (list): Array of the poll choices
                Minimum: 2 choices
                Maximum: 5 choices
            duration (int): Total duration for the poll (in seconds)
                Minimum: 15
                Maximum: 1800
            channel_points_voting_enabled (bool, optional): Indicates if Channel Points can be used for voting
                Default: false
            channel_points_per_vote (int, optional): Number of Channel Points required to vote once with Channel Points
                Minimum: 0
                Maximum: 1000000

        Raises:
            twitchpy.errors.ClientError

        Returns:
            Poll
        """

        url = ENDPOINT_POLLS
        headers = {"Authorization": f"Bearer {self.__user_token}", "Client-Id": self.client_id, "Content-Type": CONTENT_TYPE_APPLICATION_JSON}

        choices_dicts = []

        for choice in choices:
            choices_dicts.append({"title": choice})

        payload = {"broadcaster_id": broadcaster_id, "title": title, "choices": choices_dicts, "duration": duration}

        if channel_points_voting_enabled is not False:
            payload["channel_points_voting_enabled"] = channel_points_voting_enabled

        if channel_points_per_vote != 0:
            payload["channel_points_per_vote"] = channel_points_per_vote

        response = requests.post(url, headers=headers, json=payload)

        if response.ok:
            poll = response.json()["data"][0]
            poll = Poll(poll["id"], poll["broadcaster_id"], poll["broadcaster_name"], poll["broadcaster_login"], poll["title"], poll["choices"], poll["channel_points_voting_enabled"], poll["channel_points_per_vote"], poll["status"], poll["duration"], poll["started_at"])

            return poll

        else:
            raise twitchpy.errors.ClientError(response.json()["message"])

    def end_poll(self,broadcaster_id,id,status):
        """
        End a poll that is currently active

        Args:
            broadcaster_id (str): The broadcaster running polls
                                  Provided broadcaster_id must match the user_id in the user OAuth token
            id (str): ID of the poll
            status (str): The poll status to be set
                          Valid values: "TERMINATED", "ARCHIVED"

        Raises:
            twitchpy.errors.ClientError

        Returns:
            Poll
        """

        url = ENDPOINT_POLLS
        headers={"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id}
        data={"broadcaster_id":broadcaster_id,"id":id,"status":status}

        response=requests.patch(url,headers=headers,data=data)

        if response.ok:
            poll=response.json()["data"][0]
            poll=Poll(poll["id"],poll["broadcaster_id"],poll["broadcaster_name"],poll["broadcaster_login"],poll["title"],poll["choices"],poll["bits_voting_enabled"],poll["bits_per_vote"],poll["channel_points_voting_enabled"],poll["channel_points_per_vote"],poll["status"],poll["duration"],poll["started_at"])

            return poll

        else:
            raise twitchpy.errors.ClientError(response.json()["message"])

    def get_predictions(self,broadcaster_id,id=[],first=20):
        """
        Get information about all Channel Points Predictions or specific Channel Points Predictions for a Twitch channel

        Args:
            broadcaster_id (str): The broadcaster running Predictions
                                  Provided broadcaster_id must match the user_id in the user OAuth token
            id (str, optional): ID of a Prediction
                                Maximum: 100
            first (int, optional): Maximum number of objects to return
                                   Default: 20

        Raises:
            twitchpy.errors.ClientError

        Returns:
            list
        """

        url = ENDPOINT_PREDICTIONS
        headers={"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id}
        params={"broadcaster_id":broadcaster_id}

        if len(id)>0:
            params["id"]=id

        after=""
        calls=math.ceil(first/20)
        predictions=[]

        for call in range(calls):
            params["first"] = min(20, first-(20*call))

            if after!="":
                params["after"]=after

            response=requests.get(url,headers=headers,params=params)
            
            if response.ok:
                response=response.json()

                for prediction in response["data"]:
                    predictions.append(Prediction(prediction["id"],prediction["broadcaster_id"],prediction["broadcaster_name"],prediction["broadcaster_login"],prediction["title"],prediction["winning_outcome_id"],prediction["outcomes"],prediction["prediction_window"],prediction["status"],prediction["created_at"],prediction["ended_at"],prediction["locked_at"]))

                if "pagination" in response and "cursor" in response["pagination"]:
                    after=response["pagination"]["cursor"]

            else:
                raise twitchpy.errors.ClientError(response.json()["message"])

        return predictions

    def create_prediction(self, broadcaster_id: str, title: str, outcomes: list[str], prediction_window: int) -> Prediction:
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
            twitchpy.errors.ClientError

        Returns:
            Prediction
        """

        url = ENDPOINT_PREDICTIONS
        headers = {"Authorization": f"Bearer {self.__user_token}", "Client-Id": self.client_id, "Content-Type": CONTENT_TYPE_APPLICATION_JSON}
        payload={"broadcaster_id":broadcaster_id,"title":title,"prediction_window":prediction_window}

        outcomes_payload = []

        for outcome in outcomes:
            outcomes_payload.append({"title": outcome})

        payload["outcomes"] = outcomes_payload

        response=requests.post(url,headers=headers,json=payload)
        
        if response.ok:
            prediction=response.json()["data"][0]
            prediction=Prediction(prediction["id"],prediction["broadcaster_id"],prediction["broadcaster_name"],prediction["broadcaster_login"],prediction["title"],prediction["winning_outcome_id"],prediction["outcomes"],prediction["prediction_window"],prediction["status"],prediction["created_at"],prediction["ended_at"],prediction["locked_at"])

            return prediction

        else:
            raise twitchpy.errors.ClientError(response.json()["message"])

    def end_prediction(self,broadcaster_id,id,status,winning_outcome_id=""):
        """
        Lock, resolve, or cancel a Channel Points Prediction
        Active Predictions can be updated to be "locked", "resolved", or "canceled"
        Locked Predictions can be updated to be "resolved" or "canceled"

        Args:
            broadcaster_id (str): The broadcaster running prediction events
                                  Provided broadcaster_id must match the user_id in the user OAuth token
            id (str): ID of the Prediction
            status (str): The Prediction status to be set
                          Valid values: "RESOLVED", "CANCELED", "LOCKED"
            winning_outcome_id (str, optional): ID of the winning outcome for the Prediction
                                                This parameter is required if status is being set to RESOLVED

        Raises:
            twitchpy.errors.ClientError

        Returns:
            Prediction
        """

        url = ENDPOINT_PREDICTIONS
        headers={"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id}
        data={"broadcaster_id":broadcaster_id,"id":id,"status":status}

        if winning_outcome_id!="":
            data["winning_outcome_id"]=winning_outcome_id

        response=requests.patch(url,headers=headers,data=data)
        
        if response.ok:
            prediction=response.json()["data"][0]
            prediction=Prediction(prediction["id"],prediction["broadcaster_id"],prediction["broadcaster_name"],prediction["broadcaster_login"],prediction["title"],prediction["winning_outcome_id"],prediction["outcomes"],prediction["prediction_window"],prediction["status"],prediction["created_at"],prediction["ended_at"],prediction["locked_at"])

            return prediction

        else:
            raise twitchpy.errors.ClientError(response.json()["message"])

    def start_raid(self, from_broadcaster_id: str, to_broadcaster_id: str) -> dict:
        """
        Raid another channel by sending the broadcaster’s viewers to the targeted channel
        
        Args:
            from_broadcaster_id (str): The ID of the broadcaster that’s sending the raiding party
                This ID must match the user ID in the user access token
            to_broadcaster_id (str): The ID of the broadcaster to raid
        
        Returns:
            dict
        """

        url = "https://api.twitch.tv/helix/raids"
        headers = {"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id}
        payload = {"from_broadcaster_id": from_broadcaster_id, "to_broadcaster_id": to_broadcaster_id}

        response = requests.post(url, headers = headers, json = payload)

        if response.ok:
            return response.json()["data"]

        else:
            raise twitchpy.errors.ClientError(response.json()["message"])

    def cancel_raid(self, broadcaster_id: str) -> None:
        """
        Cancel a pending raid
        
        Args:
            broadcaster_id (str): The ID of the broadcaster that initiated the raid
                This ID must match the user ID in the user access token
        """

        url = "https://api.twitch.tv/helix/raids"
        headers = {"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id}
        data = {"broadcaster_id": broadcaster_id}

        requests.delete(url, headers = headers, data = data)

    def get_channel_stream_schedule(self,broadcaster_id,id=[],start_time="",utc_offset="0",first=20):
        """
        Gets all scheduled broadcasts or specific scheduled broadcasts from a channel’s stream schedule
        Scheduled broadcasts are defined as "stream segments"

        Args:
            broadcaster_id (str): User ID of the broadcaster who owns the channel streaming schedule
                                  Provided broadcaster_id must match the user_id in the user OAuth token
            id (str, optional): The ID of the stream segment to return
                                Maximum: 100
            start_time (str, optional): A timestamp in RFC3339 format to start returning stream segments from
                                        If not specified, the current date and time is used
            utc_offset (str, optional): A timezone offset for the requester specified in minutes
                                        If not specified, "0" is used for GMT
            first (int, optional): Maximum number of stream segments to return
                                   Default: 20

        Raises:
            twitchpy.errors.ClientError

        Returns:
            list
        """

        url="https://api.twitch.tv/helix/schedule"
        headers={"Authorization": f"Bearer {self.__app_token}","Client-Id":self.client_id}
        params={"broadcaster_id":broadcaster_id}

        if len(id)>0:
            params["id"]=id

        if start_time!="":
            params["start_time"]=start_time

        if utc_offset!="0":
            params["utc_offset"]=utc_offset

        after=""
        calls=math.ceil(first/25)
        schedules=[]

        for call in range(calls):
            params["first"] = min(25, first-(25*call))

            if after!="":
                params["after"]=after

            response=requests.get(url,headers=headers,params=params)
            
            if response.ok:
                response=response.json()

                for schedule in response["data"]:
                    schedules.append(StreamSchedule(schedule["segments"],schedule["broadcaster_id"],schedule["broadcaster_name"],schedule["broadcaster_login"],schedule["vacation"]))

                if "pagination" in response:
                    after=response["pagination"]["cursor"]

            else:
                raise twitchpy.errors.ClientError(response.json()["message"])

        return schedules

    def get_channel_icalendar(self, broadcaster_id):
        """
        Gets all scheduled broadcasts from a channel’s stream schedule as an iCalendar

        Args:
            broadcaster_id (str): User ID of the broadcaster who owns the channel streaming schedule

        Returns:
            str
        """

        url="https://api.twitch.tv/helix/schedule/icalendar"
        params={"broadcaster_id":broadcaster_id}

        response=requests.get(url,params=params)

        if response.ok:
            return response.text

        else:
            raise twitchpy.errors.ClientError(response.json()["message"])

    def update_channel_stream_schedule(self,broadcaster_id,is_vacation_enabled=False,vacation_start_time="",vacation_end_time="",timezone=""):
        """
        Update the settings for a channel’s stream schedule
        This can be used for setting vacation details

        Args:
            broadcaster_id (str): User ID of the broadcaster who owns the channel streaming schedule
                                  Provided broadcaster_id must match the user_id in the user OAuth token
            is_vacation_enabled (bool, optional): Indicates if Vacation Mode is enabled
                                                  Set to true to add a vacation or false to remove vacation from the channel streaming schedule
            vacation_start_time (str, optional): Start time for vacation specified in RFC3339 format
                                                 Required if is_vacation_enabled is set to true
            vacation_end_time (str, optional): End time for vacation specified in RFC3339 format
                                               Required if is_vacation_enabled is set to true
            timezone (str, optional): The timezone for when the vacation is being scheduled using the IANA time zone database format
                                      Required if is_vacation_enabled is set to true

        Raises:
            twitchpy.errors.ClientError
        """
        
        url="https://api.twitch.tv/helix/schedule/settings"
        headers={"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id}
        data={"broadcaster_id":broadcaster_id}

        if is_vacation_enabled:
            data["is_vacation_enabled"] = True

        if vacation_start_time != "":
            data["vacation_start_time"] = vacation_start_time

        if vacation_end_time != "":
            data["vacation_end_time"] = vacation_end_time

        if timezone != "":
            data["timezone"] = timezone

        requests.patch(url,headers=headers,data=data)

    def create_channel_stream_schedule_segment(self,broadcaster_id,start_time,timezone,is_recurring,duration=240,category_id="",title=""):
        """
        Create a single scheduled broadcast or a recurring scheduled broadcast for a channel’s stream schedule

        Args:
            broadcaster_id (str): User ID of the broadcaster who owns the channel streaming schedule
                                  Provided broadcaster_id must match the user_id in the user OAuth token
            start_time (str): Start time for the scheduled broadcast specified in RFC3339 format
            timezone (str): The timezone of the application creating the scheduled broadcast using the IANA time zone database format
            is_recurring (bool): Indicates if the scheduled broadcast is recurring weekly
            duration (int, optional): Duration of the scheduled broadcast in minutes from the start_time
                                      Default: 240
            category_id (str, optional): Game/Category ID for the scheduled broadcast
            title (str, optional): Title for the scheduled broadcast
                                   Maximum: 140 characters

        Raises:
            twitchpy.errors.ClientError

        Returns:
            StreamSchedule
        """
        
        url = ENDPOINT_SCHEDULE_SEGMENT
        headers={"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id}
        payload={"broadcaster_id":broadcaster_id,"start_time":start_time,"timezone":timezone,"is_recurring":is_recurring}

        if duration!=240:
            payload["duration"]=duration

        if category_id!="":
            payload["category_id"]=category_id

        if title!="":
            payload["title"]=title

        response=requests.post(url,headers=headers,json=payload)
        
        if response.ok:
            schedule=response.json()["data"][0]
            schedule=StreamSchedule(schedule["segments"],schedule["broadcaster_id"],schedule["broadcaster_name"],schedule["broadcaster_login"],schedule["vacation"])

            return schedule

        else:
            raise twitchpy.errors.ClientError(response.json()["message"])

    def update_channel_stream_schedule_segment(self,broadcaster_id,id,start_time="",duration=240,category_id="",title="",is_canceled=False,timezone=""):
        """
        Update a single scheduled broadcast or a recurring scheduled broadcast for a channel’s stream schedule

        Args:
            broadcaster_id (str): User ID of the broadcaster who owns the channel streaming schedule
                                  Provided broadcaster_id must match the user_id in the user OAuth token
            id (str): The ID of the streaming segment to update
            start_time (str, optional): Start time for the scheduled broadcast specified in RFC3339 format
            duration (int, optional): Duration of the scheduled broadcast in minutes from the start_time
                                      Default: 240
            category_id (str, optional): Game/Category ID for the scheduled broadcast
            title (str, optional): Title for the scheduled broadcast
                                   Maximum: 140 characters
            is_canceled (bool, optional): Indicated if the scheduled broadcast is canceled
            timezone (str, optional): The timezone of the application creating the scheduled broadcast using the IANA time zone database format

        Raises:
            twitchpy.errors.ClientError

        Returns:
            StreamSchedule
        """
        
        url = ENDPOINT_SCHEDULE_SEGMENT
        headers={"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id}
        data={"broadcaster_id":broadcaster_id,"id":id}

        if start_time!="":
            data["start_time"]=start_time

        if duration!=240:
            data["duration"]=duration

        if category_id!="":
            data["category_id"]=category_id

        if title!="":
            data["title"]=title

        if is_canceled!=False:
            data["is_canceled"]=is_canceled

        if timezone!="":
            data["timezone"]=timezone

        response=requests.patch(url,headers=headers,data=data)
        
        if response.ok:
            schedule=response.json()["data"][0]
            schedule=StreamSchedule(schedule["segments"],schedule["broadcaster_id"],schedule["broadcaster_name"],schedule["broadcaster_login"],schedule["vacation"])

            return schedule

        else:
            raise twitchpy.errors.ClientError(response.json()["message"])

    def delete_channel_stream_schedule_segment(self,broadcaster_id,id):
        """
        Delete a single scheduled broadcast or a recurring scheduled broadcast for a channel’s stream schedule

        Args:
            broadcaster_id (str): User ID of the broadcaster who owns the channel streaming schedule
                                  Provided broadcaster_id must match the user_id in the user OAuth token
            id (str): The ID of the streaming segment to delete
        """

        url = ENDPOINT_SCHEDULE_SEGMENT
        headers={"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id}
        data={"broadcaster_id":broadcaster_id,"id":id}

        requests.delete(url,headers=headers,data=data)

    def search_categories(self,query,first=20):
        """
        Returns a list of games or categories that match the query via name either entirely or partially

        Args:
            query (str): URI encoded search query
            first (int, optional): Maximum number of objects to return
                                   Default: 20

        Raises:
            twitchpy.errors.ClientError

        Returns:
            list
        """

        url="https://api.twitch.tv/helix/search/categories"
        headers={"Authorization": f"Bearer {self.__app_token}","Client-Id":self.client_id}
        params={"query":query}

        after=""
        calls=math.ceil(first/100)
        games=[]

        for call in range(calls):
            params["first"] = min(100, first-(100*call))

            if after!="":
                params["after"]=after

            response=requests.get(url,headers=headers,params=params)
            
            if response.ok:
                response=response.json()

                for game in response["data"]:
                    games.append(Game(game["id"],game["name"],box_art_url=game["box_art_url"]))

                if "pagination" in response:
                    after=response["pagination"]["cursor"]

            else:
                raise twitchpy.errors.ClientError(response.json()["message"])

        return games

    def search_channels(self,query,first=20,live_only=False):
        """
        Returns a list of channels (users who have streamed within the past 6 months) that match the query via channel name or description either entirely or partially

        Args:
            query (str): URI encoded search query
            first (int, optional): Maximum number of objects to return
                                   Default: 20
            live_only (bool, optional): Filter results for live streams only
                                        Default: false

        Raises:
            twitchpy.errors.ClientError

        Returns:
            list
        """

        url="https://api.twitch.tv/helix/search/channels"
        headers={"Authorization": f"Bearer {self.__app_token}","Client-Id":self.client_id}
        params={"query":query}

        if live_only!=False:
            params["live_only"]=live_only

        after=""
        calls=math.ceil(first/100)
        channels=[]

        for call in range(calls):
            params["first"] = min(100, first-(100*call))

            if after!="":
                params["after"]=after

            response=requests.get(url,headers=headers,params=params)
            
            if response.ok:
                response=response.json()

                for channel in response["data"]:
                    channels.append(Channel(channel["id"],channel["broadcaster_login"],channel["display_name"],channel["game_id"],channel["game_name"],channel["title"],broadcaster_language=channel["broadcaster_language"]))

                if "pagination" in response:
                    after=response["pagination"]["cursor"]

            else:
                raise twitchpy.errors.ClientError(response.json()["message"])

        return channels

    def get_soundtrack_current_track(self,broadcaster_id):
        """
        Gets the Soundtrack track that the broadcaster is playing

        Args:
            broadcaster_id (str): The ID of the broadcaster that’s playing a Soundtrack track

        Raises:
            twitchpy.errors.ClientError

        Returns:
            SoundtrackTrack
        """

        url="https://api.twitch.tv/helix/soundtrack/current_track"
        headers={"Authorization": f"Bearer {self.__app_token}","Client-Id":self.client_id}
        params={"broadcaster_id":broadcaster_id}

        response=requests.get(url,headers=headers,params=params)

        if response.ok:
            track=response.json()["data"][0]
            track=SoundtrackTrack(track["track"],track["source"])

            return track
        
        else:
            raise twitchpy.errors.ClientError(response.json()["message"])

    def get_soundtrack_playlist(self,id):
        """
        Gets a Soundtrack playlist, which includes its list of tracks

        Args:
            id (str): The ID of the Soundtrack playlist to get

        Raises:
            twitchpy.errors.ClientError

        Returns:
            SoundtrackPlaylist
        """

        url="https://api.twitch.tv/helix/soundtrack/playlist"
        headers={"Authorization": f"Bearer {self.__app_token}","Client-Id":self.client_id}
        params={"id":id}

        response=requests.get(url,headers=headers,params=params)

        if response.ok:
            playlist=response.json()["data"][0]
            playlist=SoundtrackPlaylist(playlist["title"],playlist["id"],playlist["image_url"],playlist["description"],playlist["tracks"])

            return playlist

        else:
            raise twitchpy.errors.ClientError(response.json()["message"])

    def get_soundtrack_playlists(self):
        """
        Gets a list of Soundtrack playlists

        Raises:
            twitchpy.errors.ClientError

        Returns:
            list
        """

        url="https://api.twitch.tv/helix/soundtrack/playlists"
        headers={"Authorization": f"Bearer {self.__app_token}","Client-Id":self.client_id}

        response=requests.get(url,headers=headers)

        if response.ok:
            playlists=[]
            
            for playlist in response.json()["data"]:
                playlists.append(SoundtrackPlaylist(playlist["title"],playlist["id"],playlist["image_url"],playlist["description"]))

            return playlists

        else:
            raise twitchpy.errors.ClientError(response.json()["message"])

    def get_stream_key(self,broadcaster_id):
        """
        Gets the channel stream key for a user

        Args:
            broadcaster_id (str): User ID of the broadcaster

        Raises:
            twitchpy.errors.ClientError

        Returns:
            str
        """

        url="https://api.twitch.tv/helix/streams/key"
        headers={"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id}
        params={"broadcaster_id":broadcaster_id}

        response=requests.get(url,headers=headers,params=params)
        
        if response.ok:
            return response.json()["data"][0]["stream_key"]

        else:
            raise twitchpy.errors.ClientError(response.json()["message"])

    def get_streams(self,first=20,game_id="",language="",user_id="",user_login=""):
        """
        Gets active streams

        Args:
            first (int, optional): Maximum number of objects to return
                                   Default: 20
            game_id (str, optional): Returns streams broadcasting a specified game ID
            language (str, optional): Stream language
                                      A language value must be either the ISO 639-1 two-letter code for a supported stream language or "other"
            user_id (str, optional): Returns streams broadcast by a specified user ID
            user_login (str, optional): Returns streams broadcast by a specified user login name

        Raises:
            twitchpy.errors.ClientError

        Returns:
            list
        """

        url="https://api.twitch.tv/helix/streams"
        headers={"Authorization": f"Bearer {self.__app_token}","Client-Id":self.client_id}
        params={}

        if game_id!="":
            params["game_id"]=game_id

        if language!="":
            params["language"]=language

        if user_id!="":
            params["user_id"]=user_id

        if user_login!="":
            params["user_login"]=user_login

        after=""
        calls=math.ceil(first/100)
        streams=[]

        for call in range(calls):
            params["first"] = min(100, first-(100*call))

            if after!="":
                params["after"]=after

            response=requests.get(url,headers=headers,params=params)

            if response.ok:
                response=response.json()

                for stream in response["data"]:
                    streams.append(Stream(stream["id"],stream["user_id"],stream["user_name"],stream["game_id"],stream["type"],stream["title"],stream["viewer_count"],stream["started_at"],stream["language"],stream["thumbnail_url"],stream["tag_ids"]))

                if "pagination" in response and "cursor" in response["pagination"]:
                    after=response["pagination"]["cursor"]

            else:
                raise twitchpy.errors.ClientError(response.json()["message"])

        return streams

    def get_followed_streams(self,user_id,first=100):
        """
        Gets information about active streams belonging to channels that the authenticated user follows

        Args:
            user_id (str): Results will only include active streams from the channels that this Twitch user follows
                           user_id must match the User ID in the bearer token
            first (int, optional): Maximum number of objects to return
                                   Default: 100

        Raises:
            twitchpy.errors.ClientError

        Returns:
            list
        """

        url="https://api.twitch.tv/helix/streams/followed"
        headers={"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id}
        params={"user_id":user_id}

        after=""
        calls=math.ceil(first/100)
        streams=[]

        for call in range(calls):
            params["first"] = min(100, first-(100*call))

            if after!="":
                params["after"]=after

            response=requests.get(url,headers=headers,params=params)
            
            if response.ok:
                response=response.json()
                
                for stream in response["data"]:
                    streams.append(Stream(stream["id"],stream["user_id"],stream["user_name"],stream["game_id"],stream["type"],stream["title"],stream["viewer_count"],stream["started_at"],stream["language"],stream["thumbnail_url"],stream["tag_ids"]))

                if "pagination" in response and "cursor" in response["pagination"]:
                    after=response["pagination"]["cursor"]

            else:
                raise twitchpy.errors.ClientError(response.json()["message"])

        return streams

    def create_stream_marker(self,user_id,description=""):
        """
        Creates a marker in the stream of a user specified by user ID
        A marker is an arbitrary point in a stream that the broadcaster wants to mark; e.g., to easily return to later
        The marker is created at the current timestamp in the live broadcast when the request is processed

        Args:
            user_id (str): ID of the broadcaster in whose live stream the marker is created
            description (str, optional): Description of or comments on the marker
                                         Max length is 140 characters

        Raises:
            twitchpy.errors.ClientError

        Returns:
            list
        """

        url="https://api.twitch.tv/helix/streams/markers"
        headers = {"Authorization": f"Bearer {self.__user_token}", "Client-Id": self.client_id, "Content-Type": CONTENT_TYPE_APPLICATION_JSON}
        payload={"user_id":user_id}

        if description!="":
            payload["description"]=description

        response=requests.post(url,headers=headers,json=payload)
        
        if response.ok:
            return response.json()["data"]

        else:
            raise twitchpy.errors.ClientError(response.json()["message"])

    def get_stream_markers(self,user_id="",video_id="",first=20):
        """
        Gets a list of markers for either a specified user’s most recent stream or a specified VOD/video (stream)
        A marker is an arbitrary point in a stream that the broadcaster wants to mark; e.g., to easily return to later
        The only markers returned are those created by the user identified by the Bearer token
        Only one of user_id and video_id must be specified

        Args:
            user_id (str, optional): ID of the broadcaster from whose stream markers are returned
            video_id (str, optional): ID of the VOD/video whose stream markers are returned
            first (int, optional): Number of values to be returned when getting videos by user or game ID
                                   Default: 20

        Raises:
            twitchpy.errors.ClientError

        Returns:
            list
        """

        url="https://api.twitch.tv/helix/streams/markers"
        headers={"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id}
        params={}

        if user_id!="":
            params["user_id"]=user_id

        if video_id!="":
            params["video_id"]=video_id

        after=""
        calls=math.ceil(first/100)
        markers=[]

        for call in range(calls):
            params["first"] = min(100, first-(100*call))

            if after!="":
                params["after"]=after

            response=requests.get(url,headers=headers,params=params)
            
            if response.ok:
                response=response.json()
                markers.extend(response["data"])

                if "pagination" in response and "cursor" in response["pagination"]:
                    after=response["pagination"]["cursor"]

            else:
                raise twitchpy.errors.ClientError(response.json()["message"])

        return markers

    def get_broadcaster_subscriptions(self,broadcaster_id,user_id=[],first=20):
        """
        Get all of a broadcaster’s subscriptions

        Args:
            broadcaster_id (str): User ID of the broadcaster
                                  Must match the User ID in the Bearer token
            user_id (list, optional): Filters results to only include potential subscriptions made by the provided user ID
                                      Accepts up to 100 values
            first (int, optional): Maximum number of objects to return
                                   Default: 20

        Raises:
            twitchpy.errors.ClientError

        Returns:
            list
        """

        url="https://api.twitch.tv/helix/subscriptions"
        headers={"Authorization":f"Bearer {self.__user_token}","Client-Id":self.client_id}
        params={"broadcaster_id":broadcaster_id}

        if len(user_id)>0:
            params["user_id"]=user_id

        if first!=20:
            params["first"]=first

        after=""
        calls=math.ceil(first/100)
        subscriptions=[]

        for call in range(calls):
            if first-(100*call)>100:
                params["first"]=100
            
            else:
                params["first"]=first-(100*call)

            if after!="":
                params["after"]=after

            response=requests.get(url,headers=headers,params=params)
            
            if response.ok:
                response=response.json()
                subscriptions.extend(response["data"])

                if "pagination" in response:
                    after=response["pagination"]["cursor"]

            else:
                raise twitchpy.errors.ClientError(response.json()["message"])

        return subscriptions

    def check_user_subscription(self,broadcaster_id,user_id):
        """
        Checks if a specific user (user_id) is subscribed to a specific channel (broadcaster_id)

        Args:
            broadcaster_id (str): User ID of an Affiliate or Partner broadcaster
            user_id (str): User ID of a Twitch viewer

        Raises:
            twitchpy.errors.ClientError

        Returns:
            dict
        """
        
        url="https://api.twitch.tv/helix/subscriptions/user"
        headers={"Authorization":f"Bearer {self.__user_token}","Client-Id":self.client_id}
        params={"broadcaster_id":broadcaster_id,"user_id":user_id}

        response=requests.get(url,headers=headers,params=params)
        
        if response.ok:
            return response.json()["data"][0]

        else:
            raise twitchpy.errors.ClientError(response.json()["message"])

    def get_all_stream_tags(self,first=20,tag_id=[]):
        """
        Gets the list of all stream tags defined by Twitch

        Args:
            first (int, optional): Maximum number of objects to return
                                   Default: 20
            tag_id (list, optional): ID of a tag

        Raises:
            twitchpy.errors.ClientError

        Returns:
            list
        """

        url="https://api.twitch.tv/helix/tags/streams"
        headers={"Authorization":f"Bearer {self.__app_token}","Client-Id":self.client_id}
        params={}

        if len(tag_id)>0:
            params["tag_id"]=tag_id

        after=""
        calls=math.ceil(first/100)
        tags=[]

        for call in range(calls):
            params["first"] = min(100, first-(100*call))

            if after!="":
                params["after"]=after

            response=requests.get(url,headers=headers,params=params)
            
            if response.ok:
                response=response.json()

                for tag in response["data"]:
                    tags.append(Tag(tag["tag_id"],tag["is_auto"],tag["localization_names"],tag["localization_descriptions"]))

                if "pagination" in response:
                    after=response["pagination"]["cursor"]

            else:
                raise twitchpy.errors.ClientError(response.json()["message"])

        return tags

    def get_stream_tags(self,broadcaster_id):
        """
        Gets the list of current stream tags that have been set for a channel

        Args:
            broadcaster_id (str): User ID of the channel to get tags

        Raises:
            twitchpy.errors.ClientError

        Returns:
            list
        """

        url="https://api.twitch.tv/helix/streams/tags"
        headers={"Authorization": f"Bearer {self.__app_token}","Client-Id":self.client_id}
        params={"broadcaster_id":broadcaster_id}

        response=requests.get(url,headers=headers,params=params)
        
        if response.ok:
            response=response.json()
            tags=[]

            for tag in response["data"]:
                tags.append(Tag(tag["tag_id"],tag["is_auto"],tag["localization_names"],tag["localization_descriptions"]))

            return tags

        else:
            raise twitchpy.errors.ClientError(response.json()["message"])

    def replace_stream_tags(self,broadcaster_id,tag_ids=[]):
        """
        Applies specified tags to a specified stream (channel), overwriting any existing tags applied to that stream
        If no tags are specified, all tags previously applied to the stream are removed
        Automated tags are not affected by this operation

        Args:
            broadcaster_id (str): ID of the stream for which tags are to be replaced
            tag_ids (list, optional): IDs of tags to be applied to the stream
        """

        url="https://api.twitch.tv/helix/streams/tags"
        headers = {"Authorization": f"Bearer {self.__user_token}", "Client-Id": self.client_id, "Content-Type": CONTENT_TYPE_APPLICATION_JSON}
        data={"broadcaster_id":broadcaster_id}

        if len(tag_ids)>0:
            data["tag_ids"]=tag_ids

        requests.put(url,headers=headers,data=data)

    def get_channel_teams(self,broadcaster_id):
        """
        Retrieves a list of Twitch Teams of which the specified channel/broadcaster is a member

        Args:
            broadcaster_id (str): User ID for a Twitch user

        Raises:
            twitchpy.errors.ClientError

        Returns:
            list
        """

        url="https://api.twitch.tv/helix/teams/channel"
        headers={"Authorization": f"Bearer {self.__app_token}","Client-Id":self.client_id}
        params={"broadcaster_id":broadcaster_id}

        response=requests.get(url,headers=headers,params=params)
        
        if response.ok:
            teams=[]

            for team in response.json()["data"]:
                teams.append(self.get_teams(id=team["id"]))

            return teams

        else:
            raise twitchpy.errors.ClientError(response.json()["message"])

    def get_teams(self,name="",id=""):
        """
        Gets information for a specific Twitch Team
        One of the two optional query parameters must be specified to return Team information

        Args:
            name (str, optional): Team name
            id (str, optional): Team ID

        Raises:
            twitchpy.errors.ClientError

        Returns:
            Team
        """

        url="https://api.twitch.tv/helix/teams"
        headers={"Authorization": f"Bearer {self.__app_token}","Client-Id":self.client_id}
        params={}

        if name!="":
            params["name"]=name

        if id!="":
            params["id"]=id

        response=requests.get(url,headers=headers,params=params)
        
        if response.ok:
            team=response.json()["data"][0]
            users=[]

            for user in team["users"]:
                users.append(User(user["user_id"],user["user_login"],user["user_name"]))

            team=Team(users,team["background_image_url"],team["banner"],team["created_at"],team["updated_at"],team["info"],team["thumbnail_url"],team["team_name"],team["team_display_name"],team["id"])

            return team
                
        else:
            raise twitchpy.errors.ClientError(response.json()["message"])

    def get_users(self,id=[],login=[]):
        """
        Gets an user
        Users are identified by optional user IDs and/or login name
        If neither a user ID nor a login name is specified, the user is looked up by Bearer token

        Args:
            id (list, optional): User ID
                                 Limit: 100
            login (list, optional): User login name
                                    Limit: 100

        Raises:
            twitchpy.errors.ClientError

        Returns:
            list
        """

        url="https://api.twitch.tv/helix/users"
        headers={"Authorization": f"Bearer {self.__app_token}","Client-Id":self.client_id}
        params={}

        if len(id)>0:
            params["id"]=id

        if len(login)>0:
            aux=[]

            for i in range(len(login)):
                aux.append(login[i].replace("@","").lower())

            params["login"]=aux

        response=requests.get(url,headers=headers,params=params)
        
        if response.ok:
            users=[]

            for user in response.json()["data"]:
                users.append(User(user["id"],user["login"],user["display_name"],user["type"],user["broadcaster_type"],user["description"],user["profile_image_url"],user["offline_image_url"],user["view_count"]))
            
            return users

        else:
            raise twitchpy.errors.ClientError(response.json()["message"])

    def update_user(self,description=""):
        """
        Updates the description of a user specified by the bearer token
        If the description parameter is not provided, no update will occur and the current user data is returned

        Args:
            description (str, optional): User’s account description

        Raises:
            twitchpy.errors.ClientError

        Returns:
            User
        """

        url="https://api.twitch.tv/helix/users"
        headers={"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id}
        data={}

        if description!="":
            data={"description":description}

        response=requests.put(url,headers=headers,data=data)

        if response.ok:
            user=response.json()["data"][0]
            user=User(user["id"],user["login"],user["display_name"],user["type"],user["broadcaster_type"],user["description"],user["profile_image_url"],user["offline_image_url"],user["view_count"])

            return user

        else:
            raise twitchpy.errors.ClientError(response.json()["message"])

    def get_user_follows(self,first=20,from_id="",to_id=""):
        """
        Gets information on follow relationships between two Twitch users
        At minimum, from_id or to_id must be provided for a query to be valid

        Args:
            first (int, optional): Maximum number of objects to return
                                   Default: 20
            from_id (str, optional): User ID
                                     The request returns information about users who are being followed by the from_id user
            to_id (str, optional): User ID
                                   The request returns information about users who are following the to_id user

        Raises:
            twitchpy.errors.ClientError

        Returns:
            list
        """

        url="https://api.twitch.tv/helix/users/follows"
        headers={"Authorization": f"Bearer {self.__app_token}","Client-Id":self.client_id}
        params={}

        if first!=20:
            params["first"]=first

        if from_id!="":
            params["from_id"]=from_id

        if to_id!="":
            params["to_id"]=to_id

        after=""
        calls=math.ceil(first/100)
        follow=[]

        for call in range(calls):
            if first-(100*call)>100:
                params["first"]=100
            
            else:
                params["first"]=first-(100*call)

            if after!="":
                params["after"]=after

            response=requests.get(url,headers=headers,params=params)
            
            if response.ok:
                response=response.json()
                follow.extend(response["data"])

                if "pagination" in response:
                    after=response["pagination"]["cursor"]

            else:
                raise twitchpy.errors.ClientError(response.json()["message"])

        return follow

    def get_user_block_list(self,broadcaster_id,first=20):
        """
        Gets a specified user’s block list

        Args:
            broadcaster_id (str): User ID for a Twitch user
            first (int, optional): Maximum number of objects to return
                                   Default: 20

        Raises:
            twitchpy.errors.ClientError

        Returns:
            list
        """

        url = ENDPOINT_USER_BLOCKS
        headers={"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id}
        params={"broadcaster_id":broadcaster_id}

        if first!=20:
            params["first"]=first

        after=""
        calls=math.ceil(first/100)
        ids=[]

        for call in range(calls):
            if first-(100*call)>100:
                params["first"]=100
            
            else:
                params["first"]=first-(100*call)

            if after!="":
                params["after"]=after

            response=requests.get(url,headers=headers,params=params)
            
            if response.ok:
                for user in response.json()["data"]:
                    ids.append(user["user_id"])

            else:
                raise twitchpy.errors.ClientError(response.json()["message"])

        return self.get_users(id=ids)

    def block_user(self,target_user_id,source_context="",reason=""):
        """
        Blocks the specified user on behalf of the authenticated user

        Args:
            target_user_id (str): User ID of the user to be blocked
            source_context (str, optional): Source context for blocking the user
                                            Valid values: "chat", "whisper"
            reason (str, optional): Reason for blocking the user
                                    Valid values: "spam", "harassment", or "other"
        """

        url = ENDPOINT_USER_BLOCKS
        headers={"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id}
        data={"target_user_id":target_user_id}

        if source_context!="":
            data["source_context"]=source_context

        if reason!="":
            data["reason"]=reason

        requests.put(url,headers=headers,data=data)

    def unblock_user(self,target_user_id):
        """
        Unblocks the specified user on behalf of the authenticated user

        Args:
            target_user_id (str): User ID of the user to be unblocked
        """

        url = ENDPOINT_USER_BLOCKS
        headers={"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id}
        data={"target_user_id":target_user_id}

        requests.delete(url,headers=headers,data=data)

    def get_user_extensions(self):
        """
        Gets a list of all extensions (both active and inactive) for a specified user, identified by a Bearer token

        Raises:
            twitchpy.errors.ClientError

        Returns:
            list
        """

        url="https://api.twitch.tv/helix/users/extensions/list"
        headers={"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id}

        response=requests.get(url,headers=headers)
        
        if response.ok:
            return response.json()["data"]

        else:
            raise twitchpy.errors.ClientError(response.json()["message"])

    def get_user_active_extensions(self,user_id=""):
        """
        Gets information about active extensions installed by a specified user, identified by a user ID or Bearer token

        Args:
            user_id (str, optional): ID of the user whose installed extensions will be returned

        Raises:
            twitchpy.errors.ClientError

        Returns:
            list
        """

        url="https://api.twitch.tv/helix/users/extensions"
        headers={"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id}
        params={}

        if user_id!="":
            params={"user_id":user_id}

        response=requests.get(url,headers=headers,params=params)
        
        if response.ok:
            return response.json()["data"]

        else:
            raise twitchpy.errors.ClientError(response.json()["message"])

    def update_user_extensions(self):
        """
        Updates the activation state, extension ID, and/or version number of installed extensions for a specified user, identified by a Bearer token
        If you try to activate a given extension under multiple extension types, the last write wins (and there is no guarantee of write order)

        Raises:
            twitchpy.errors.ClientError

        Returns:
            list
        """

        url="https://api.twitch.tv/helix/users/extensions"
        headers = {"Authorization": f"Bearer {self.__user_token}", "Client-Id": self.client_id, "Content-Type": CONTENT_TYPE_APPLICATION_JSON}

        response=requests.put(url,headers=headers)
        
        if response.ok:
            return response.json()["data"]

        else:
            raise twitchpy.errors.ClientError(response.json()["message"])

    def get_videos(self,id=[],user_id="",game_id="",first=20,language="",period="all",sort="time",type="all"):
        """
        Gets video information by video ID, user ID, or game ID
        Each request must specify one video id, one user_id, or one game_id

        Args:
            id (list): ID of the video being queried
                       Limit: 100
                       If this is specified, you cannot use first, language, period, sort and type
            user_id (str): ID of the user who owns the video
            game_id (str): ID of the game the video is of
            first (int, optional): Number of values to be returned when getting videos by user or game ID
                                   Default: 20
            language (str, optional): Language of the video being queried
                                      A language value must be either the ISO 639-1 two-letter code for a supported stream language or "other"
            period (str, optional): Period during which the video was created
                                    Valid values: "all", "day", "week", "month"
            sort (str, optional): Sort order of the videos
                                  Valid values: "time", "trending", "views"
                                  Default: "time"
            type (str, optional): Type of video
                                  Valid values: "all", "upload", "archive", "highlight"
                                  Default: "all"

        Raises:
            twitchpy.errors.ClientError

        Returns:
            list
        """

        url="https://api.twitch.tv/helix/videos"
        headers={"Authorization": f"Bearer {self.__app_token}","Client-Id":self.client_id}
        params={}

        if len(id)>0:
            params["id"]=id

        if user_id!="":
            params["user_id"]=user_id

        if game_id!="":
            params["game_id"]=game_id

        if language!="":
            params["language"]=language

        if period!="all":
            params["period"]=period

        if sort!="time":
            params["sort"]=sort

        if type!="all":
            params["type"]=type

        after=""
        calls=math.ceil(first/100)
        videos=[]

        for call in range(calls):
            params["first"] = min(100, first-(100*call))

            if after!="":
                params["after"]=after

            response=requests.get(url,headers=headers,params=params)
            
            if response.ok:
                response=response.json()

                for video in response["data"]:
                    videos.append(Video(video["id"],video["user_id"],video["user_name"],video["title"],video["description"],video["created_at"],video["published_at"],video["url"],video["thumbnail_url"],video["viewable"],video["view_count"],video["language"],video["type"],video["duration"]))

                if "pagination" in response:
                    after=response["pagination"]["cursor"]

            else:
                raise twitchpy.errors.ClientError(response.json()["message"])

        return videos

    def delete_video(self,id):
        """
        Deletes a video
        Videos are past broadcasts, Highlights, or uploads

        Args:
            id (str): ID of the video(s) to be deleted
                      Limit: 5
        """

        url="https://api.twitch.tv/helix/videos"
        headers={"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id}
        data={"id":id}

        requests.delete(url,headers=headers,data=data)

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
        """

        url = "https://api.twitch.tv/helix/whispers"
        headers = {"Authorization": f"Bearer {self.__user_token}", "Client-Id": self.client_id, "Content-Type": "application/json"}
        payload = {"from_user_id": from_user_id, "to_user_id": to_user_id, "message": message}

        requests.post(url, headers=headers, json=payload)

    def get_webhook_subscriptions(self,first=20):
        """
        Gets the Webhook subscriptions of an application identified by a Bearer token, in order of expiration

        Args:
            first (int, optional): Number of values to be returned
                                   Default: 20

        Raises:
            twitchpy.errors.ClientError

        Returns:
            list
        """

        url="https://api.twitch.tv/helix/webhooks/subscriptions"
        headers={"Authorization": f"Bearer {self.__app_token}","Client-Id":self.client_id}
        params={}

        if first!=20:
            params={"first":first}

        after=""
        calls=math.ceil(first/100)
        subscriptions=[]

        for call in range(calls):
            if first-(100*call)>100:
                params["first"]=100
            
            else:
                params["first"]=first-(100*call)

            if after!="":
                params["after"]=after

            response=requests.get(url,headers=headers,params=params)
            
            if response.ok:
                response=response.json()
                subscriptions.extend(response["data"])

                if "pagination" in response and "cursor" in response["pagination"]:
                    after=response["pagination"]["cursor"]

            else:
                raise twitchpy.errors.ClientError(response.json()["message"])

        return subscriptions