import requests
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

class Client:
    """
    Represents a client connection to the Twitch API
    """

    def __init__(self,oauth_token,client_id,client_secret,code=""):
        """
        Args:
            oauth_token (str): OAuth Token
            client_id (str): Client ID
            client_secret (str): Client secret
            code (str, optional): Authorization code
        """
        
        self.oauth_token=oauth_token
        self.client_id=client_id
        self.client_secret=client_secret
        self.__app_token=self.__get_app_token()

        if code!="" or os.path.isfile(os.path.dirname(os.path.realpath(__file__))+"/tokens.secret"):
            self.__user_token,self.__refresh_user_token=self.__get_user_token(code)

        else:
            self.__user_token=""
            self.__refresh_user_token=""

    def __get_app_token(self):
        url="https://id.twitch.tv/oauth2/token"
        payload={"client_id":self.client_id,"client_secret":self.client_secret,"grant_type":"client_credentials"}

        response=requests.post(url,json=payload).json()

        return response["access_token"]

    def __get_user_token(self,code):
        try:
            secret_file=open(os.path.dirname(os.path.realpath(__file__))+"/tokens.secret","rt")
            secrets=secret_file.readlines()
            secret_file.close()

            for i in range(len(secrets)):
                secret=secrets[i].split("=")

                if "USER_TOKEN"==secret[0]:
                    self.__user_token=secret[1].replace("\n","")

                if "REFRESH_USER_TOKEN"==secret[0]:
                    self.__refresh_user_token=secret[1].replace("\n","")

            url="https://id.twitch.tv/oauth2/token"
            payload={"grant_type":"refresh_token","refresh_token":self.__refresh_user_token,"client_id":self.client_id,"client_secret":self.client_secret}

            response=requests.post(url,json=payload).json()

            secret_file=open(os.path.dirname(os.path.realpath(__file__))+"/tokens.secret","rt")
            secrets=secret_file.readlines()
            secret_file.close()

            data=""

            for i in range(len(secrets)):
                secret=secrets[i].split("=")

                if "USER_TOKEN"==secret[0]:
                    secrets[i]=f"USER_TOKEN={response['access_token']}\n"

                if "REFRESH_USER_TOKEN"==secret[0]:
                    secrets[i]=f"REFRESH_USER_TOKEN={response['refresh_token']}"

                data+=secrets[i]

            secret_file=open(os.path.dirname(os.path.realpath(__file__))+"/tokens.secret","wt")
            secret_file.write(data)
            secret_file.close()

        except FileNotFoundError:
            try:
                url=f"https://id.twitch.tv/oauth2/token?client_id={self.client_id}&client_secret={self.client_secret}&code={code}&grant_type=authorization_code&redirect_uri=https://localhost"

                response=requests.post(url).json()

                data=f"USER_TOKEN={response['access_token']}\nREFRESH_USER_TOKEN={response['refresh_token']}"

                secret_file=open(os.path.dirname(os.path.realpath(__file__))+"/tokens.secret","wt")
                secret_file.write(data)
                secret_file.close()

            except KeyError:
                raise twitchpy.errors.InvalidCodeError("Invalid code")

        except KeyError:
            raise twitchpy.errors.InvalidCodeError("Invalid code")

        except AttributeError:
            raise twitchpy.errors.InvalidCodeError("Invalid code")

        return response["access_token"],response["refresh_token"]

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
            list
        """

        url="https://api.twitch.tv/helix/channels/commercial"
        headers={"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id,"Content-Type":"application/json"}
        payload={"broadcaster_id":broadcaster_id,"length":length}

        response=requests.post(url,headers=headers,json=payload).json()

        try:
            if len(response["data"])>0:
                return response["data"]

            else:
                return None
        
        except KeyError:
            raise twitchpy.errors.ClientError(response["message"])

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

        if first!=20:
            params["first"]=first

        if started_at!="":
            params["started_at"]=started_at

        if type!="":
            params["type"]=type

        after=""

        calls=math.ceil(first/100)

        output=[]

        for call in range(calls):
            if first-(100*call)>100:
                params["first"]=100
            
            else:
                params["first"]=first-(100*call)

            if after!="":
                params["after"]=after

            response=requests.get(url,headers=headers,params=params).json()

            try:
                if len(response["data"])>0:
                    output.extend(response["data"])

                    if bool(response["pagination"])==True:
                        after=response["pagination"]["cursor"]

                else:
                    return None

            except KeyError:
                raise twitchpy.errors.ClientError(response["message"])

        return output

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

        if first!=20:
            params["first"]=first

        if game_id!="":
            params["game_id"]=game_id

        if started_at!="":
            params["started_at"]=started_at

        if type!="":
            params["type"]=type

        after=""

        calls=math.ceil(first/100)

        output=[]

        for call in range(calls):
            if first-(100*call)>100:
                params["first"]=100
            
            else:
                params["first"]=first-(100*call)

            if after!="":
                params["after"]=after

            response=requests.get(url,headers=headers,params=params).json()

            try:
                if len(response["data"])>0:
                    output.extend(response["data"])

                    if bool(response["pagination"])==True:
                        after=response["pagination"]["cursor"]

                else:
                    return None

            except KeyError:
                raise twitchpy.errors.ClientError(response["message"])

        return output

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

        response=requests.get(url,headers=headers,params=params).json()

        try:
            if len(response["data"])>0:
                return response["data"]

            else:
                return None

        except KeyError:
            raise twitchpy.errors.ClientError(response["message"])

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

        if broadcaster_id=="":
            response=requests.get(url,headers=headers).json()

        else:
            params={"broadcaster_id":broadcaster_id}
            response=requests.get(url,headers=headers,params=params).json()

        try:
            if len(response["data"])>0:
                return response["data"]

            else:
                return None

        except KeyError:
            raise twitchpy.errors.ClientError(response["message"])
        
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

        output=[]

        for call in range(calls):
            if first-(100*call)>100:
                params["first"]=100
            
            else:
                params["first"]=first-(100*call)

            if after!="":
                params["after"]=after

            response=requests.get(url,headers=headers,params=params).json()

            try:
                if len(response["data"])>0:
                    output.extend(response["data"])

                    if bool(response["pagination"])==True:
                        after=response["pagination"]["cursor"]

                else:
                    return None

            except KeyError:
                raise twitchpy.errors.ClientError(response["message"])

        return output

    def get_channel(self,broadcaster_id):
        """
        Gets a channel

        Args:
            broadcaster_id (str): ID of the channel to be updated

        Raises:
            twitchpy.errors.ClientError

        Returns:
            Channel
        """

        url="https://api.twitch.tv/helix/channels"
        headers={"Authorization": f"Bearer {self.__app_token}","Client-Id":self.client_id}
        params={"broadcaster_id":broadcaster_id}

        response=requests.get(url,headers=headers,params=params).json()

        try:
            if len(response["data"])>0:
                channel=response["data"][0]
                channel=Channel(self.oauth_token,self.client_id,self.client_secret,"",channel["broadcaster_login"],channel["game_name"],channel["broadcaster_language"],channel["title"])
                
                return channel

            else:
                return None

        except KeyError:
            raise twitchpy.errors.ClientError(response["message"])

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

        if game_id=="" and broadcaster_language=="" and title=="" and delay==0:
            raise twitchpy.errors.FewArgumentsError("game_id, broadcaster_language, title or delay must be provided")

        if game_id!="":
            data["game_id"]=game_id

        if broadcaster_language!="":
            data["broadcaster_language"]=broadcaster_language

        if title!="":
            data["title"]=title

        if delay!=0:
            data["delay"]=delay

        response=requests.patch(url,headers=headers,data=data)

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

        response=requests.get(url,headers=headers,params=params).json()

        try:
            if len(response["data"])>0:
                ids=[]

                for user in response["data"]:
                    ids.append(user["user_id"])

                users=self.get_users(id=ids)

                return users

            else:
                return None

        except KeyError:
            raise twitchpy.errors.ClientError(response["message"])

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
            list
        """

        url="https://api.twitch.tv/helix/channel_points/custom_rewards"
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

        response=requests.post(url,headers=headers,params=params).json()

        try:
            if len(response["data"])>0:
                rewards=[]

                for reward in response["data"]:
                    rewards.append(Reward(reward["broadcaster_name"],reward["broadcaster_id"],reward["id"],reward["image"],reward["background_color"],reward["is_enabled"],reward["cost"],reward["title"],reward["prompt"],reward["is_user_input_required"],reward["max_per_stream_setting"],reward["max_per_user_per_stream_setting"],reward["global_cooldown_setting"],reward["is_paused"],reward["is_in_stock"],reward["default_image"],reward["should_redemptions_skip_request_queue"],reward["redemptions_redeemed_current_stream"],reward["cooldown_expires_at"]))

                return rewards

            else:
                return None

        except KeyError:
            raise twitchpy.errors.ClientError(response["message"])

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

        url="https://api.twitch.tv/helix/channel_points/custom_rewards"
        headers={"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id}
        data={"broadcaster_id":broadcaster_id,"id":id}

        response=requests.delete(url,headers=headers,data=data)

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

        response=requests.get(url,headers=headers,params=params).json()

        try:
            if len(response["data"])>0:
                rewards=[]

                for reward in response["data"]:
                    rewards.append(Reward(reward["broadcaster_name"],reward["broadcaster_id"],reward["id"],reward["image"],reward["background_color"],reward["is_enabled"],reward["cost"],reward["title"],reward["prompt"],reward["is_user_input_required"],reward["max_per_stream_setting"],reward["max_per_user_per_stream_setting"],reward["global_cooldown_setting"],reward["is_paused"],reward["is_in_stock"],reward["default_image"],reward["should_redemptions_skip_request_queue"],reward["redemptions_redeemed_current_stream"],reward["cooldown_expires_at"]))

                return rewards

            else:
                return None

        except KeyError:
            raise twitchpy.errors.ClientError(response["message"])

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

        if first!=20:
            params["first"]=first

        after=""

        calls=math.ceil(first/50)

        redemptions=[]

        for call in range(calls):
            if first-(50*call)>50:
                params["first"]=50
            
            else:
                params["first"]=first-(50*call)

            if after!="":
                params["after"]=after

            response=requests.get(url,headers=headers,params=params).json()

            try:
                if len(response["data"])>0:
                    for redemption in response["data"]:
                        redemptions.append(Redemption(redemption["broadcaster_name"],redemption["broadcaster_id"],redemption["id"],redemption["user_id"],redemption["user_name"],redemption["user_input"],redemption["status"],redemption["redeemed_at"],self.get_custom_reward(redemption["broadcaster_id"],[redemption["reward"]["id"]])[0]))

                else:
                    return None

            except KeyError:
                raise twitchpy.errors.ClientError(response["message"])
        
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
            list
        """

        url="https://api.twitch.tv/helix/channel_points/custom_rewards"
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

        response=requests.patch(url,headers=headers,data=data).json()

        try:
            if len(response["data"])>0:
                rewards=[]

                for reward in response["data"]:
                    rewards.append(Reward(reward["broadcaster_name"],reward["broadcaster_id"],reward["id"],reward["image"],reward["background_color"],reward["is_enabled"],reward["cost"],reward["title"],reward["prompt"],reward["is_user_input_required"],reward["max_per_stream_setting"],reward["max_per_user_per_stream_setting"],reward["global_cooldown_setting"],reward["is_paused"],reward["is_in_stock"],reward["default_image"],reward["should_redemptions_skip_request_queue"],reward["redemptions_redeemed_current_stream"],reward["cooldown_expires_at"]))

                return rewards

            else:
                return None

        except KeyError:
            raise twitchpy.errors.ClientError(response["message"])

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
            list
        """

        url="https://api.twitch.tv/helix/channel_points/custom_rewards/redemptions"
        headers={"Authorization":f"Bearer {self.__user_token}","Client-Id":self.client_id}
        data={"id":id,"broadcaster_id":broadcaster_id,"reward_id":reward_id}

        if status!="":
            data["status"]=status

        response=requests.patch(url,headers=headers,data=data).json()

        try:
            if len(response["data"])>0:
                redemption=Redemption(response["data"][0]["broadcaster_name"],response["data"][0]["broadcaster_id"],response["data"][0]["id"],response["data"][0]["user_id"],response["data"][0]["user_name"],response["data"][0]["user_input"],response["data"][0]["status"],response["data"][0]["redeemed_at"],response["data"][0]["reward"])
                
                return redemption

            else:
                return None

        except KeyError:
            raise twitchpy.errors.ClientError(response["message"])

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

        response=requests.get(url,headers=headers,params=params).json()

        try:
            if len(response["data"])>0:
                return response["data"]

        except KeyError:
            raise twitchpy.errors.ClientError(response["message"])

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

        response=requests.get(url,headers=headers).json()

        try:
            if len(response["data"])>0:
                return response["data"]

        except KeyError:
            raise twitchpy.errors.ClientError(response["message"])

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

        response=requests.get(url,headers=headers,params=params).json()

        try:
            if len(response["data"])>0:
                return response["data"]

        except KeyError:
            raise twitchpy.errors.ClientError(response["message"])

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

        response=requests.get(url,headers=headers,params=params).json()

        try:
            if len(response["data"])>0:
                return response["data"]

            else:
                return None

        except KeyError:
            raise twitchpy.errors.ClientError(response["message"])

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

        response=requests.get(url,headers=headers).json()

        try:
            if len(response["data"])>0:
                return response["data"]

            else:
                return None

        except KeyError:
            raise twitchpy.errors.ClientError(response["message"])

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

        response=requests.post(url,headers=headers,json=payload).json()

        try:
            if len(response["data"])>0:
                return response["data"][0]

            else:
                return None

        except KeyError:
            raise twitchpy.errors.ClientError(response["message"])

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

        if first!=20:
            params["first"]=first

        if started_at!="":
            params["started_at"]=started_at

        after=""

        calls=math.ceil(first/100)

        output=[]

        for call in range(calls):
            if first-(100*call)>100:
                params["first"]=100
            
            else:
                params["first"]=first-(100*call)

            if after!="":
                params["after"]=after

            response=requests.get(url,headers=headers,params=params).json()

            try:
                if len(response["data"])>0:
                    output.extend(response["data"])

                    if bool(response["pagination"])==True:
                        after=response["pagination"]["cursor"]

                else:
                    return None

            except KeyError:
                raise twitchpy.errors.ClientError(response["message"])

        return output

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

        response=requests.get(url,headers=headers,params=params).json()

        try:
            if len(response["data"])>0:
                return response["data"]

            else:
                return None

        except KeyError:
            raise twitchpy.errors.ClientError(response["message"])

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
            params["fulfullment_status"]=fulfillment_status

        if first!=20:
            params["first"]=first

        after=""

        calls=math.ceil(first/1000)

        output=[]

        for call in range(calls):
            if first-(1000*call)>1000:
                params["first"]=1000
            
            else:
                params["first"]=first-(1000*call)

            if after!="":
                params["after"]=after

            response=requests.get(url,headers=headers,params=params).json()

            try:
                if len(response["data"])>0:
                    output.extend(response["data"])

                    if bool(response["pagination"])==True:
                        after=response["pagination"]["cursor"]

                else:
                    return None

            except KeyError:
                raise twitchpy.errors.ClientError(response["message"])

        return output

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
        headers={"Authorization":f"Bearer {self.__app_token}","Client-Id":self.client_id,"Content-Type":"application/json"}
        data={}

        if len(entitlement_ids)>0:
            data["entitlement_ids"]=entitlement_ids

        if fulfillment_status!="":
            data["fulfillment_status"]=fulfillment_status

        response=requests.patch(url,headers=headers,data=data).json()

        try:
            if len(response["data"])>0:
                return response["data"]

            else:
                return None

        except KeyError:
            raise twitchpy.errors.ClientError(response["message"])

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

        response=requests.post(url,headers=headers,json=payload).json()

        try:
            if len(response["data"])>0:
                return response["data"]

            else:
                return None

        except KeyError:
            raise twitchpy.errors.ClientError(response["message"])

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
            dict
        """

        url="https://api.twitch.tv/helix/eventsub/subscriptions"
        headers={"Authorization":f"Bearer {self.__app_token}","Client-Id":self.client_id,"Content-Type":"application/json"}
        payload={"type":type,"version":version,"condition":condition,"transport":transport}

        response=requests.post(url,headers=headers,json=payload).json()

        try:
            if len(response["data"])>0:
                return response["data"][0]

            else:
                return None

        except KeyError:
            raise twitchpy.errors.ClientError(response["message"])

    def delete_eventsub_subscription(self,id):
        """
        Delete an EventSub subscription

        Args:
            id (str): The subscription ID for the subscription to delete
        """

        url="https://api.twitch.tv/helix/eventsub/subscriptions"
        headers={"Authorization":f"Bearer {self.__app_token}","Client-Id":self.client_id}
        data={"id":id}

        response=requests.delete(url,headers=headers,data=data)

    def get_eventsub_subscriptions(self,status="",type=""):
        """
        Get a list of your EventSub subscriptions
        Only include one filter query parameter

        Args:
            status (str, optional): Filters subscriptions by one status type
                                    Valid values: "enabled", "webhook_callback_verification_pending", "webhook_callback_verification_failed", "notification_failures_exceeded", "authorization_revoked", "user_removed"
            type (str, optional): Filters subscriptions by subscription type name

        Raises:
            twitchpy.errors.ClientError

        Returns:
            list
        """
        
        url="https://api.twitch.tv/helix/eventsub/subscriptions"
        headers={"Authorization":f"Bearer {self.__app_token}","Client-Id":self.client_id}
        params={}

        if status!="":
            params["status"]=status

        if type!="":
            params["type"]=type

        response=requests.get(url,headers=headers,params=params).json()

        try:
            if len(response["data"])>0:
                return response["data"]

            else:
                return None

        except KeyError:
            raise twitchpy.errors.ClientError(response["message"])

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

        if first!=20:
            params={"first":first}

        after=""

        calls=math.ceil(first/100)

        games=[]

        for call in range(calls):
            if first-(100*call)>100:
                params["first"]=100
            
            else:
                params["first"]=first-(100*call)

            if after!="":
                params["after"]=after

            response=requests.get(url,headers=headers,params=params).json()
            
            try:
                for game in response["data"]:
                    games.append(self.get_games(id=game["id"])[0])

            except KeyError:
                raise twitchpy.errors.ClientError(response["message"])

        return games

    def get_games(self,id=[],name=[]):
        """
        Gets games by game ID or name
        For a query to be valid, name and/or id must be specified

        Args:
            id (list, optional): Game ID
                                 At most 100 id values can be specified
            name (list, optional): Game name
                                   The name must be an exact match
                                   At most 100 name values can be specified

        Raises:
            twitchpy.errors.ClientError

        Returns:
            list
        """

        url="https://api.twitch.tv/helix/games"
        headers={"Authorization": f"Bearer {self.__app_token}","Client-Id":self.client_id}
        params={}

        if len(id)>0:
            params["id"]=id

        if len(name)>0:
            params["name"]=name

        response=requests.get(url,headers=headers,params=params).json()

        try:
            if len(response["data"])>0:
                games=[]

                for game in response["data"]:
                    games.append(Game(game["id"],game["name"],game["box_art_url"]))

            else:
                return None

        except KeyError:
            raise twitchpy.errors.ClientError(response["message"])

        return games

    def get_hype_train_events(self,broadcaster_id,first=1,id=""):
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
            id (str, optional): The id of the wanted event

        Raises:
            twitchpy.errors.ClientError

        Returns:
            list
        """

        url="https://api.twitch.tv/helix/hypetrain/events"
        headers={"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id}
        params={"broadcaster_id":broadcaster_id}

        if first!=1:
            params["first"]=first

        if id!="":
            params["id"]=id
        
        cursor=""

        calls=math.ceil(first/100)

        output=[]

        for call in range(calls):
            if first-(100*call)>100:
                params["first"]=100
            
            else:
                params["first"]=first-(100*call)

            if cursor!="":
                params["cursor"]=cursor

            response=requests.get(url,headers=headers,params=params).json()

            try:
                if len(response["data"])>0:
                    output.extend(response["data"])

                    if bool(response["pagination"])==True:
                        cursor=response["pagination"]["cursor"]

                else:
                    return None

            except KeyError:
                raise twitchpy.errors.ClientError(response["message"])

        return output

    def check_automod_status(self,broadcaster_id,msg_id,msg_user,user_id):
        """
        Determines whether a string message meets the channel’s AutoMod requirements

        Args:
            broadcaster_id (str): Provided broadcaster_id must match the user_id in the auth token
            msg_id (str, optional): Developer-generated identifier for mapping messages to results
            msg_user (str, optional): Message text
            user_id (str, optional): User ID of the sender

        Raises:
            twitchpy.errors.ClientError

        Returns:
            list
        """

        url="https://api.twitch.tv/helix/moderation/enforcements/status"
        headers={"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id}
        payload={"broadcaster_id":broadcaster_id,"data":[{"msg_id":msg_id,"msg_user":msg_user,"user_id":user_id}]}

        response=requests.post(url,headers=headers,json=payload).json()

        try:
            if len(response["data"])>0:
                return response["data"]

            else:
                return None

        except KeyError:
            raise twitchpy.errors.ClientError(response["message"])

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

        response=requests.post(url,headers=headers,json=payload)

    def get_banned_events(self,broadcaster_id,user_id=[],first=20):
        """
        Returns all user bans and un-bans in a channel

        Args:
            broadcaster_id (str): Provided broadcaster_id must match the user_id in the auth token
            user_id (list, optional): Filters the results and only returns a status object for ban events that include users being banned or un-banned in this channel and have a matching user_id
                                      Maximum: 100
            first (int, optional): Maximum number of objects to return
                                   Default: 20

        Raises:
            twitchpy.errors.ClientError

        Returns:
            list
        """

        url="https://api.twitch.tv/helix/moderation/banned/events"
        headers={"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id}
        params={"broadcaster_id":broadcaster_id}

        if len(user_id)>0:
            params["user_id"]=user_id

        if first!=20:
            params["first"]=first

        after=""

        calls=math.ceil(first/100)

        output=[]

        for call in range(calls):
            if first-(100*call)>100:
                params["first"]=100
            
            else:
                params["first"]=first-(100*call)

            if after!="":
                params["after"]=after

            response=requests.get(url,headers=headers,params=params).json()

            try:
                if len(response["data"])>0:
                    output.extend(response["data"])

                    if bool(response["pagination"])==True:
                        after=response["pagination"]["cursor"]

                else:
                    return None

            except KeyError:
                raise twitchpy.errors.ClientError(response["message"])

        return output

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

        output=[]

        for call in range(calls):
            if first-(100*call)>100:
                params["first"]=100
            
            else:
                params["first"]=first-(100*call)

            if after!="":
                params["after"]=after

            response=requests.get(url,headers=headers,params=params).json()

            try:
                if len(response["data"])>0:
                    output.extend(response["data"])

                    if bool(response["pagination"])==True:
                        after=response["pagination"]["cursor"]

                else:
                    return None

            except KeyError:
                raise twitchpy.errors.ClientError(response["message"])

        return output

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

        if first!=20:
            params["first"]=first

        after=""

        calls=math.ceil(first/100)

        for call in range(calls):
            if first-(100*call)>100:
                params["first"]=100
            
            else:
                params["first"]=first-(100*call)

            if after!="":
                params["after"]=after

            response=requests.get(url,headers=headers,params=params).json()

            try:
                if len(response["data"])>0:
                    ids=[]

                    for user in response["data"]:
                        ids.append(user["user_id"])
                    
                    users=self.get_users(id=ids)

                else:
                    return None

            except KeyError:
                raise twitchpy.errors.ClientError(response["message"])

        return users

    def get_moderator_events(self,broadcaster_id,user_id=[],first=20):
        """
        Returns a list of moderators or users added and removed as moderators from a channel

        Args:
            broadcaster_id (str): Provided broadcaster_id must match the user_id in the auth token
            user_id (list, optional): Filters the results and only returns a status object for users who have been added or removed as moderators in this channel and have a matching user_id
                                      Maximum: 100
            first (int, optional): Maximum number of objects to return
                                   Default: 20

        Raises:
            twitchpy.errors.ClientError

        Returns:
            list
        """

        url="https://api.twitch.tv/helix/moderation/moderators/events"
        headers={"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id}
        params={"broadcaster_id":broadcaster_id}

        if len(user_id)>0:
            params["user_id"]=user_id

        if first!=20:
            params["first"]=first

        after=""

        calls=math.ceil(first/100)

        output=[]

        for call in range(calls):
            if first-(100*call)>100:
                params["first"]=100
            
            else:
                params["first"]=first-(100*call)

            if after!="":
                params["after"]=after

            response=requests.get(url,headers=headers,params=params).json()

            try:
                if len(response["data"])>0:
                    output.extend(response["data"])

                    if bool(response["pagination"])==True:
                        after=response["pagination"]["cursor"]

                else:
                    return None

            except KeyError:
                raise twitchpy.errors.ClientError(response["message"])

        return output

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

        url="https://api.twitch.tv/helix/polls"
        headers={"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id}
        params={"broadcaster_id":broadcaster_id}

        if len(id)>0:
            params["id"]=id

        if first!=20:
            params["first"]=first

        after=""

        calls=math.ceil(first/20)

        output=[]

        for call in range(calls):
            if first-(20*call)>20:
                params["first"]=20
            
            else:
                params["first"]=first-(20*call)

            if after!="":
                params["after"]=after

            response=requests.get(url,headers=headers,params=params).json()

            try:
                if response["data"]!=None and len(response["data"])>0:
                    output.extend(response["data"])

                    if bool(response["pagination"])==True:
                        after=response["pagination"]["cursor"]

                else:
                    return None

            except KeyError:
                raise twitchpy.errors.ClientError(response["message"])

        return output

    def create_poll(self,broadcaster_id,title,choices,duration,bits_voting_enabled=False,bits_per_vote=0,channel_points_voting_enabled=False,channel_points_per_vote=0):
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
            bits_voting_enabled (bool, optional): Indicates if Bits can be used for voting
                                                  Default: false
            bits_per_vote (int, optional): Number of Bits required to vote once with Bits
                                           Minimum: 0
                                           Maximum: 10000
            channel_points_voting_enabled (bool, optional): Indicates if Channel Points can be used for voting
                                                            Default: false
            channel_points_per_vote (int, optional): Number of Channel Points required to vote once with Channel Points
                                                     Minimum: 0
                                                     Maximum: 1000000

        Raises:
            twitchpy.errors.ClientError

        Returns:
            dict
        """
        
        url="https://api.twitch.tv/helix/polls"
        headers={"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id,"Content-Type":"application/json"}
        payload={"broadcaster_id":broadcaster_id,"title":title,"choices":choices,"duration":duration}

        if bits_voting_enabled!=False:
            payload["bits_voting_enabled"]=bits_voting_enabled

        if bits_per_vote!=0:
            payload["bits_per_vote"]=bits_per_vote

        if channel_points_voting_enabled!=False:
            payload["channel_points_voting_enabled"]=channel_points_voting_enabled

        if channel_points_per_vote!=0:
            payload["channel_points_per_vote"]=channel_points_per_vote

        response=requests.post(url,headers=headers,json=payload).json()

        try:
            if len(response["data"])>0:
                return response["data"][0]

            else:
                return None

        except KeyError:
            raise twitchpy.errors.ClientError(response["message"])

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
            dict
        """

        url="https://api.twitch.tv/helix/polls"
        headers={"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id}
        data={"broadcaster_id":broadcaster_id,"id":id,"status":status}

        response=requests.patch(url,headers=headers,data=data).json()

        try:
            if len(response["data"])>0:
                return response["data"][0]

            else:
                return None

        except KeyError:
            raise twitchpy.errors.ClientError(response["message"])

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

        url="https://api.twitch.tv/helix/predictions"
        headers={"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id}
        params={"broadcaster_id":broadcaster_id}

        if len(id)>0:
            params["id"]=id

        if first!=20:
            params["first"]=first

        after=""

        calls=math.ceil(first/20)

        output=[]

        for call in range(calls):
            if first-(20*call)>20:
                params["first"]=20
            
            else:
                params["first"]=first-(20*call)

            if after!="":
                params["after"]=after

            response=requests.get(url,headers=headers,params=params).json()

            try:
                if response["data"]!=None and len(response["data"])>0:
                    output.extend(response["data"])

                    if bool(response["pagination"])==True:
                        after=response["pagination"]["cursor"]

                else:
                    return None

            except KeyError:
                raise twitchpy.errors.ClientError(response["message"])

        return output

    def create_prediction(self,broadcaster_id,title,outcomes,prediction_window):
        """
        Create a Channel Points Prediction for a specific Twitch channel

        Args:
            broadcaster_id (str): The broadcaster running Predictions
                                  Provided broadcaster_id must match the user_id in the user OAuth token
            title (str): Title for the Prediction
                         Maximum: 45 characters
            outcomes (list): Array of outcome objects with titles for the Prediction
                             Array size must be 2
                             The first outcome object is the "blue" outcome and the second outcome object is the "pink" outcome when viewing the Prediction on Twitch
            prediction_window (int): Total duration for the Prediction (in seconds)
                                     Minimum: 1
                                     Maximum: 1800

        Raises:
            twitchpy.errors.ClientError

        Returns:
            dict
        """

        url="https://api.twitch.tv/helix/predictions"
        headers={"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id,"Content-Type":"application/json"}
        payload={"broadcaster_id":broadcaster_id,"title":title,"outcomes":outcomes,"prediction_window":prediction_window}

        response=requests.post(url,headers=headers,json=payload).json()

        try:
            if len(response["data"])>0:
                return response["data"][0]

            else:
                return None

        except KeyError:
            raise twitchpy.errors.ClientError(response["message"])

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
            dict
        """

        url="https://api.twitch.tv/helix/predictions"
        headers={"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id}
        data={"broadcaster_id":broadcaster_id,"id":id,"status":status}

        if winning_outcome_id!="":
            data["winning_outcome_id"]=winning_outcome_id

        response=requests.patch(url,headers=headers,data=data).json()

        try:
            if len(response["data"])>0:
                return response["data"][0]

            else:
                return None

        except KeyError:
            raise twitchpy.errors.ClientError(response["message"])

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

        if first!=20:
            params["first"]=first

        after=""

        calls=math.ceil(first/25)

        output=[]

        for call in range(calls):
            if first-(25*call)>25:
                params["first"]=25
            
            else:
                params["first"]=first-(25*call)

            if after!="":
                params["after"]=after

            response=requests.get(url,headers=headers,params=params).json()

            try:
                if len(response["data"])>0:
                    output.extend(response["data"])

                    if bool(response["pagination"])==True:
                        after=response["pagination"]["cursor"]

                else:
                    return None

            except KeyError:
                raise twitchpy.errors.ClientError(response["message"])

        return output

    def get_channel_iCalendar(self,broadcaster_id):
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

        if response.status_code==200:
            return response.text

        else:
            return None

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

        Returns:
            dict
        """
        
        url="https://api.twitch.tv/helix/schedule/settings"
        headers={"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id}
        data={"broadcaster_id":broadcaster_id}

        response=requests.patch(url,headers=headers,data=data)

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
            dict
        """
        
        url="https://api.twitch.tv/helix/schedule/segment"
        headers={"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id}
        payload={"broadcaster_id":broadcaster_id,"start_time":start_time,"timezone":timezone,"is_recurring":is_recurring}

        if duration!=240:
            payload["duration"]=duration

        if category_id!="":
            payload["category_id"]=category_id

        if title!="":
            payload["title"]=title

        response=requests.post(url,headers=headers,json=payload).json()

        try:
            if len(response["data"])>0:
                return response["data"][0]

            else:
                return None

        except KeyError:
            raise twitchpy.errors.ClientError(response["message"])

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
            dict
        """
        
        url="https://api.twitch.tv/helix/schedule/segment"
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

        response=requests.patch(url,headers=headers,data=data).json()

        try:
            if len(response["data"])>0:
                return response["data"][0]

            else:
                return None

        except KeyError:
            raise twitchpy.errors.ClientError(response["message"])

    def delete_channel_stream_schedule_segment(self,broadcaster_id,id):
        """
        Delete a single scheduled broadcast or a recurring scheduled broadcast for a channel’s stream schedule

        Args:
            broadcaster_id (str): User ID of the broadcaster who owns the channel streaming schedule
                                  Provided broadcaster_id must match the user_id in the user OAuth token
            id (str): The ID of the streaming segment to delete
        """

        url="https://api.twitch.tv/helix/schedule/segment"
        headers={"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id}
        data={"broadcaster_id":broadcaster_id,"id":id}

        response=requests.delete(url,headers=headers,data=data)

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

        if first!=20:
            params["first"]=first

        after=""

        calls=math.ceil(first/100)

        games=[]

        for call in range(calls):
            if first-(100*call)>100:
                params["first"]=100
            
            else:
                params["first"]=first-(100*call)

            if after!="":
                params["after"]=after

            response=requests.get(url,headers=headers,params=params).json()

            try:
                if len(response["data"])>0:
                    for game in response["data"]:
                        games.append(self.get_games(id=game["id"])[0])

                else:
                    return None

            except KeyError:
                raise twitchpy.errors.ClientError(response["message"])

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

        if first!=20:
            params["first"]=first

        if live_only!=False:
            params["live_only"]=live_only

        after=""

        calls=math.ceil(first/100)

        channels=[]

        for call in range(calls):
            if first-(100*call)>100:
                params["first"]=100
            
            else:
                params["first"]=first-(100*call)

            if after!="":
                params["after"]=after

            response=requests.get(url,headers=headers,params=params).json()

            try:
                if len(response["data"])>0:
                    for channel in response["data"]:
                        channels.append(self.get_channel(channel["id"]))

                else:
                    return None

            except KeyError:
                raise twitchpy.errors.ClientError(response["message"])

        return channels

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

        response=requests.get(url,headers=headers,params=params).json()

        try:
            if len(response["data"])>0:
                return response["data"][0]["stream_key"]

            else:
                return None

        except KeyError:
            raise twitchpy.errors.ClientError(response["message"])

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

        if first!=20:
            params["first"]=first

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
            if first-(100*call)>100:
                params["first"]=100
            
            else:
                params["first"]=first-(100*call)

            if after!="":
                params["after"]=after

            response=requests.get(url,headers=headers,params=params).json()

            try:
                if len(response["data"])>0:
                    for stream in response["data"]:
                        streams.append(Stream(stream["id"],stream["user_id"],stream["user_name"],stream["game_id"],stream["type"],stream["title"],stream["viewer_count"],stream["started_at"],stream["language"],stream["thumbnail_url"],stream["tag_ids"]))

                else:
                    return None

            except KeyError:
                raise twitchpy.errors.ClientError(response["message"])

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

        if first!=100:
            params["first"]=first

        after=""

        calls=math.ceil(first/100)

        streams=[]

        for call in range(calls):
            if first-(100*call)>100:
                params["first"]=100
            
            else:
                params["first"]=first-(100*call)

            if after!="":
                params["after"]=after

            response=requests.get(url,headers=headers,params=params).json()

            try:
                if len(response["data"])>0:
                    for stream in response["data"]:
                        streams.append(Stream(stream["id"],stream["user_id"],stream["user_name"],stream["game_id"],stream["type"],stream["title"],stream["viewer_count"],stream["started_at"],stream["language"],stream["thumbnail_url"],stream["tag_ids"]))

            except KeyError:
                raise twitchpy.errors.ClientError(response["message"])

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
        headers={"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id,"Content-Type":"application/json"}
        payload={"user_id":user_id}

        if description!="":
            payload["description"]=description

        response=requests.post(url,headers=headers,json=payload).json()

        try:
            if len(response["data"])>0:
                return response["data"]

            else:
                return None

        except KeyError:
            raise twitchpy.errors.ClientError(response["message"])

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

        if first!=20:
            params["first"]=first

        after=""

        calls=math.ceil(first/100)

        output=[]

        for call in range(calls):
            if first-(100*call)>100:
                params["first"]=100
            
            else:
                params["first"]=first-(100*call)

            if after!="":
                params["after"]=after

            response=requests.get(url,headers=headers,params=params).json()

            try:
                if len(response["data"])>0:
                    output.extend(response["data"])

                    if bool(response["pagination"])==True:
                        after=response["pagination"]["cursor"]

                else:
                    return None

            except KeyError:
                raise twitchpy.errors.ClientError(response["message"])

        return output

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

        output=[]

        for call in range(calls):
            if first-(100*call)>100:
                params["first"]=100
            
            else:
                params["first"]=first-(100*call)

            if after!="":
                params["after"]=after

            response=requests.get(url,headers=headers,params=params).json()

            try:
                if len(response["data"])>0:
                    output.extend(response["data"])

                    if bool(response["pagination"])==True:
                        after=response["pagination"]["cursor"]

                else:
                    return None

            except KeyError:
                raise twitchpy.errors.ClientError(response["message"])

        return output

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

        response=requests.get(url,headers=headers,params=params).json()

        try:
            if len(response["data"])>0:
                return response["data"][0]

            else:
                return None

        except KeyError:
            raise twitchpy.errors.ClientError(response["message"])

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

        if first!=20:
            params["first"]=first

        if len(tag_id)>0:
            params["tag_id"]=tag_id

        after=""

        calls=math.ceil(first/100)

        output=[]

        for call in range(calls):
            if first-(100*call)>100:
                params["first"]=100
            
            else:
                params["first"]=first-(100*call)

            if after!="":
                params["after"]=after

            response=requests.get(url,headers=headers,params=params).json()

            try:
                if len(response["data"])>0:
                    output.extend(response["data"])

                    if bool(response["pagination"])==True:
                        after=response["pagination"]["cursor"]

                else:
                    return None

            except KeyError:
                raise twitchpy.errors.ClientError(response["message"])

        return output

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

        response=requests.get(url,headers=headers,params=params).json()

        try:
            if len(response["data"])>0:
                return response["data"]

            else:
                return None

        except KeyError:
            raise twitchpy.errors.ClientError(response["message"])

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
        headers={"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id,"Content-Type":"application/json"}
        data={"broadcaster_id":broadcaster_id}

        if len(tag_ids)>0:
            data["tag_ids"]=tag_ids

        response=requests.put(url,headers=headers,data=data)

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

        response=requests.get(url,headers=headers,params=params).json()

        try:
            if response["data"]!=None and len(response["data"])>0:
                teams=[]

                for user in response["data"]:
                    teams.append(self.get_teams(id=user["id"]))

                return teams

            else:
                return None

        except KeyError:
            raise twitchpy.errors.ClientError(response["message"])

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

        response=requests.get(url,headers=headers,params=params).json()

        try:
            if len(response["data"])>0:
                team=response["data"][0]
                team=Team(team["users"],team["background_image_url"],team["banner"],team["created_at"],team["updated_at"],team["info"],team["thumbnail_url"],team["team_name"],team["team_display_name"],team["id"])

                return team
                
            else:
                return None

        except KeyError:
            raise twitchpy.errors.ClientError(response["message"])

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

        response=requests.get(url,headers=headers,params=params).json()

        try:
            if len(response["data"])>0:
                users=[]

                for user in response["data"]:
                    users.append(User(user["id"],user["login"],user["display_name"],user["type"],user["broadcaster_type"],user["description"],user["profile_image_url"],user["offline_image_url"],user["view_count"]))
                
                return users

            else:
                return None

        except KeyError:
            raise twitchpy.errors.ClientError(response["message"])

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

        if description=="":
            response=requests.put(url,headers=headers).json()

        else:
            data={"description":description}

            response=requests.put(url,headers=headers,data=data).json()

        try:
            if len(response["data"])>0:
                user=self.get_users(id=[response["data"][0]["id"]])

                return user

            else:
                return None

        except KeyError:
            raise twitchpy.errors.ClientError(response["message"])

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

        output=[]

        for call in range(calls):
            if first-(100*call)>100:
                params["first"]=100
            
            else:
                params["first"]=first-(100*call)

            if after!="":
                params["after"]=after

            response=requests.get(url,headers=headers,params=params).json()

            try:
                if len(response["data"])>0:
                    output.extend(response["data"])

                    if bool(response["pagination"])==True:
                        after=response["pagination"]["cursor"]

                else:
                    return None

            except KeyError:
                raise twitchpy.errors.ClientError(response["message"])

        return output

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

        url="https://api.twitch.tv/helix/users/blocks"
        headers={"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id}
        params={"broadcaster_id":broadcaster_id}

        if first!=20:
            params["first"]=first

        after=""

        calls=math.ceil(first/100)

        for call in range(calls):
            if first-(100*call)>100:
                params["first"]=100
            
            else:
                params["first"]=first-(100*call)

            if after!="":
                params["after"]=after

            response=requests.get(url,headers=headers,params=params).json()

            try:
                if len(response["data"])>0:
                    ids=[]

                    for user in response["data"]:
                        ids.append(user["user_id"])

                    users=self.get_users(id=ids)

                else:
                    return None

            except KeyError:
                raise twitchpy.errors.ClientError(response["message"])

        return users

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

        url="https://api.twitch.tv/helix/users/blocks"
        headers={"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id}
        data={"target_user_id":target_user_id}

        if source_context!="":
            data["source_context"]=source_context

        if reason!="":
            data["reason"]=reason

        response=requests.put(url,headers=headers,data=data)

    def unblock_user(self,target_user_id):
        """
        Unblocks the specified user on behalf of the authenticated user

        Args:
            target_user_id (str): User ID of the user to be unblocked
        """

        url="https://api.twitch.tv/helix/users/blocks"
        headers={"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id}
        data={"target_user_id":target_user_id}

        response=requests.delete(url,headers=headers,data=data)

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

        response=requests.get(url,headers=headers).json()

        try:
            if len(response["data"])>0:
                return response["data"]

            else:
                return None

        except KeyError:
            raise twitchpy.errors.ClientError(response["message"])

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

        if user_id=="":
            response=requests.get(url,headers=headers).json()

        else:
            params={"user_id":user_id}

            response=requests.get(url,headers=headers,params=params).json()

        try:
            if len(response["data"])>0:
                return response["data"]

            else:
                return None

        except KeyError:
            raise twitchpy.errors.ClientError(response["message"])

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
        headers={"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id,"Content-Type":"application/json"}

        response=requests.put(url,headers=headers).json()

        try:
            if len(response["data"])>0:
                return response["data"]

            else:
                return None

        except KeyError:
            raise twitchpy.errors.ClientError(response["message"])

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

        if first!=20:
            params["first"]=first

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
            if first-(100*call)>100:
                params["first"]=100
            
            else:
                params["first"]=first-(100*call)

            if after!="":
                params["after"]=after

            response=requests.get(url,headers=headers,params=params).json()

            try:
                if len(response["data"])>0:
                    for video in response["data"]:
                        videos.append(Video(video["id"],video["user_id"],video["user_name"],video["title"],video["description"],video["created_at"],video["published_at"],video["url"],video["thumbnail_url"],video["viewable"],video["view_count"],video["language"],video["type"],video["duration"]))

                else:
                    return None

            except KeyError:
                raise twitchpy.errors.ClientError(response["message"])

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

        response=requests.delete(url,headers=headers,data=data)

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

        output=[]

        for call in range(calls):
            if first-(100*call)>100:
                params["first"]=100
            
            else:
                params["first"]=first-(100*call)

            if after!="":
                params["after"]=after

            response=requests.get(url,headers=headers,params=params).json()

            try:
                if len(response["data"])>0:
                    output.extend(response["data"])

                    if bool(response["pagination"])==True:
                        after=response["pagination"]["cursor"]

                else:
                    return None

            except KeyError:
                raise twitchpy.errors.ClientError(response["message"])

        return output