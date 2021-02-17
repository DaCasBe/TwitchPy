import requests
from twitchpy.user import User
from twitchpy.game import Game
from twitchpy.stream import Stream
from twitchpy.channel import Channel
import os
from twitchpy.reward import Reward
from twitchpy.redemption import Redemption
import twitchpy.errors

class Client:
    """
    Represents a client connection to the Twitch API
    """

    def __init__(self,app_token,client_id,client_secret,code=""):
        """
        Args:
            app_token (str): OAuth Token
            client_id (str): Client ID
            client_secret (str): Client secret
            code (str, optional): Code
        """
        
        self.app_token=app_token
        self.client_id=client_id
        self.client_secret=client_secret
        self.__app_token=self.__get_app_token()
        self.__user_token,self.__refresh_user_token=self.__get_user_token(code)

    def __get_app_token(self):
        """
        Method for obtaining a Twitch API app token

        Returns:
            str
        """

        url="https://id.twitch.tv/oauth2/token"
        payload={"client_id":self.client_id,"client_secret":self.client_secret,"grant_type":"client_credentials"}

        response=requests.post(url,json=payload).json()

        return response["access_token"]

    def __get_user_token(self,code):
        """
        Method for obtaining a Twitch API user token

        Returns:
            str, str
        """

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

    def get_extension_analytics(self,extension_id="",first=20,type=""):
        """
        Gets a URL that extension developers can use to download analytics reports for their extensions
        The URL is valid for 5 minutes

        Args:
            extension_id (str, optional): Client ID value assigned to the extension when it is created
            first (int, optional): Maximum number of objects to return
                                   Maximum: 100
            type (str, optional): Type of analytics report that is returned
                                  Valid values: "overview_v1" and "overview_v2"

        Returns:
            list
        """

        url="https://api.twitch.tv/helix/analytics/extensions"
        headers={"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id}

        if extension_id=="" and first==20 and type=="":
            response=requests.get(url,headers=headers).json()

        else:
            params={}

            if extension_id!="":
                params["extension_id"]=extension_id

            if first!=20:
                params["first"]=first

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

    def get_game_analytics(self,first=20,game_id="",type=""):
        """
        Gets a URL that game developers can use to download analytics reports for their games
        The URL is valid for 5 minutes

        Args:
            first (int, optional): Maximum number of objects to return
                                   Maximum: 100
            game_id (str, optional): Game ID
            type (str, optional): Type of analytics report that is returned
                                  Valid values: "overview_v1" and "overview_v2"

        Returns:
            list
        """

        url="https://api.twitch.tv/helix/analytics/games"
        headers={"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id}

        if first==20 and game_id=="" and type=="":
            response=requests.get(url,headers=headers).json()

        else:
            params={}

            if first!=20:
                params["first"]=first

            if game_id!="":
                params["game_id"]=game_id

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

    def get_bits_leaderboard(self,count=10,user_id=""):
        """
        Gets a ranked list of Bits leaderboard information for a broadcaster

        Args:
            count (int, optional): Number of results to be returned
                                   Maximum: 100
                                   Default: 10
            user_id (str, optional): ID of the user whose results are returned

        Returns:
            list
        """

        url="https://api.twitch.tv/helix/bits/leaderboard"
        headers={"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id}

        if count==10 and user_id=="":
            response=requests.get(url,headers=headers).json()

        else:
            params={}

            if count!=10:
                params["count"]=count

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
        
    def get_extension_transactions(self,extension_id,id="",first=20):
        """
        Allows extension back end servers to fetch a list of transactions that have occurred for their extension across all of Twitch

        Args:
            extension_id (str): ID of the extension to list transactions for
            id (str, optional): Transaction IDs to look up
            first (int, optional): Maximum number of objects to return
                                   Maximum: 100
                                   Default: 20

        Returns:
            list
        """

        url="https://api.twitch.tv/helix/extensions/transactions"
        headers={"Authorization": f"Bearer {self.__app_token}","Client-Id":self.client_id}
        params={"extension_id":extension_id}

        if id!="":
            params["id"]=id

        if first!=20:
            params["first"]=first

        response=requests.get(url,headers=headers,params=params).json()

        try:
            if len(response["data"])>0:
                return response["data"]

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
                                         Defaults true
            background_color (str, optional): Custom background color for the reward
                                              Format: Hex with # prefix
            is_user_input_required (bool, optional): Does the user need to enter information when redeeming the reward
                                                     Defaults false
            is_max_per_stream_enabled (bool, optional): Whether a maximum per stream is enabled
                                                        Defaults to false
            max_per_stream (int, optional): The maximum number per stream if enabled
            is_max_per_user_per_stream_enabled (bool, optional): Whether a maximum per user per stream is enabled
                                                                 Defaults to false
            max_per_user_per_stream (int, optional): The maximum number per user per stream if enabled
            is_global_cooldown_enabled (bool, optional): Whether a cooldown is enabled
                                                         Defaults to false
            global_cooldown_seconds (int, optional): The cooldown in seconds if enabled
            should_redemptions_skip_request_queue (bool, optional): Should redemptions be set to FULFILLED status immediately when redeemed and skip the request queue instead of the normal UNFULFILLED status
                                                                    Defaults false

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
        Any UNFULFILLED Custom Reward Redemptions of the deleted Custom Reward will be updated to the FULFILLED status

        Args:
            broadcaster_id (str): ID of the channel deleting a reward
            id (str): ID of the Custom Reward to delete
        """

        url="https://api.twitch.tv/helix/channel_points/custom_rewards"
        headers={"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id}
        data={"broadcaster_id":broadcaster_id,"id":id}

        response=requests.delete(url,headers=headers,data=data)

    def get_custom_reward(self,broadcaster_id,id="",only_manageable_rewards=False):
        """
        Returns a list of Custom Reward objects for the Custom Rewards on a channel

        Args:
            broadcaster_id (str): ID of the channel deleting a reward
            id (str, optional): This parameter filters the results and only returns reward objects for the Custom Rewards with matching ID
            only_manageable_rewards (bool, optional): When set to true, only returns custom rewards that the calling broadcaster can manage
                                                      Defaults false.

        Returns:
            list
        """

        url=f"https://api.twitch.tv/helix/channel_points/custom_rewards"
        headers={"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id}
        params={"broadcaster_id":broadcaster_id}

        if id!="":
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

    def get_custom_reward_redemption(self,broadcaster_id,reward_id,id="",status="",sort="OLDEST",first=20):
        """
        Returns Custom Reward Redemption objects for a Custom Reward on a channel
        You may specify only one of the args

        Args:
            broadcaster_id (str): ID of the channel owner of a reward
            reward_id (str): This parameter returns paginated Custom Reward Redemption objects for redemptions of the Custom Reward
            id (str, optional): This param filters the results and only returns Custom Reward Redemption objects for the redemptions with matching ID
            status (str, optional): This param filters the paginated Custom Reward Redemption objects for redemptions with the matching status
                                    Can be one of UNFULFILLED, FULFILLED or CANCELED
            sort (str, optional): Sort order of redemptions returned when getting the paginated Custom Reward Redemption objects for a reward
                                  One of: OLDEST, NEWEST
                                  Default: OLDEST
            first (int, optional): Number of results to be returned when getting the paginated Custom Reward Redemption objects for a reward
                                   Limit: 50
                                   Default: 20

        Returns:
            list
        """

        url="https://api.twitch.tv/helix/channel_points/custom_rewards/redemptions"
        headers={"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id}
        params={"broadcaster_id":broadcaster_id,"reward_id":reward_id}

        if id!="":
            params["id"]=id

        if status!="":
            params["status"]=status

        if sort!="OLDEST":
            params["sort"]=sort

        if first!=20:
            params["first"]=first

        response=requests.get(url,headers=headers,params=params).json()

        try:
            if len(response["data"])>0:
                redemptions=[]

                for redemption in response["data"]:
                    redemptions.append(Redemption(redemption["broadcaster_name"],redemption["broadcaster_id"],redemption["id"],redemption["user_id"],redemption["user_name"],redemption["user_input"],redemption["status"],redemption["redeemed_at"],redemption["reward"]))
                
                return redemptions

            else:
                return None

        except KeyError:
            raise twitchpy.errors.ClientError(response["message"])

    def update_custom_reward(self,broadcaster_id,id,title="",prompt="",cost=None,background_color="",is_enabled=None,is_user_input_required=None,is_max_per_stream_enabled=None,max_per_stream=None,is_max_per_user_per_stream_enabled=False,max_per_user_per_stream=None,is_global_cooldown_enabled=False,global_cooldown_seconds=None,is_paused=None,should_redemptions_skip_request_queue=None):
        """
        Updates a Custom Reward created on a channel

        Args:
            broadcaster_id (str): ID of the channel updating a reward
            id (str): ID of the Custom Reward to update
            title (str, optional): The title of the reward
            prompt (str, optional): The prompt for the viewer when they are redeeming the reward
            cost (int, optional): The cost of the reward
            background_color (str, optional): Custom background color for the reward
                                              Format: Hex with # prefix
            is_enabled (bool, optional): Is the reward currently enabled
            is_user_input_required (bool, optional): Does the user need to enter information when redeeming the reward
            is_max_per_stream_enabled (bool, optional): Whether a maximum per stream is enabled
            max_per_stream (int, optional): The maximum number per stream if enabled
            is_max_per_user_per_stream_enabled (bool, optional): Whether a maximum per user per stream is enabled
                                                                 Defaults to false
            max_per_user_per_stream (int, optional): The maximum number per user per stream if enabled
            is_global_cooldown_enabled (bool, optional): Whether a cooldown is enabled
                                                         Defaults to false
            global_cooldown_seconds (int, optional): The cooldown in seconds if enabled
            is_paused (bool, optional): Is the reward currently paused
            should_redemptions_skip_request_queue (bool, optional): Should redemptions be set to FULFILLED status immediately when redeemed and skip the request queue instead of the normal UNFULFILLED status

        Returns:
            list
        """

        url="https://api.twitch.tv/helix/channel_points/custom_rewards"
        headers={"Authorization":f"Bearer {self.__user_token}","Client-Id":self.client_id,"Content-Type":"application/json"}
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

        if is_global_cooldown_enabled!=False:
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

        Args:
            id (str): ID of the Custom Reward Redemption to update
            broadcaster_id (str): ID of the channel updating a reward redemption
            reward_id (str): ID of the Custom Reward the redemptions to be updated are for
            status (str, optional): The new status to set redemptions to
                                    Can be either FULFILLED or CANCELED

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

    def create_clip(self,broadcaster_id,has_delay=False):
        """
        This returns both an ID and an edit URL for a new clip.

        Args:
            broadcaster_id (str): ID of the stream from which the clip will be made
            has_delay (bool, optional): If false, the clip is captured from the live stream when the API is called; otherwise, a delay is added before the clip is captured (to account for the brief delay between the broadcaster’s stream and the viewer’s experience of that stream)
                                        Default: false.

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

    def get_clips(self,broadcaster_id="",game_id="",id="",first=20):
        """
        Gets clip information by clip ID, broadcaster ID or game ID (one only)

        Args:
            broadcaster_id (str, optional): ID of the broadcaster for whom clips are returned
            game_id (str, optional): ID of the game for which clips are returned
            id (str, optional): ID of the clip being queried
            first (int, optional): Maximum number of objects to return
                                   Maximum: 100
                                   Default: 20

        Returns:
            list
        """

        url="https://api.twitch.tv/helix/clips"
        headers={"Authorization":f"Bearer {self.__user_token}","Client-Id":self.client_id}

        if broadcaster_id=="" and game_id=="" and id=="" and first==20:
            response=requests.get(url,headers=headers).json()

        else:
            if (broadcaster_id!="" and game_id!="") or (broadcaster_id!="" and id!="") or (game_id!="" and id!="") or (broadcaster_id!="" and game_id!="" and id!=""):
                raise twitchpy.errors.TooManyArgumentsError("Too many arguments have been given")

            params={}

            if broadcaster_id!="":
                params["broadcaster_id"]=broadcaster_id

            if game_id!="":
                params["game_id"]=game_id

            if id!="":
                params["id"]=id

            if first!=20:
                params["first"]=first

            response=requests.get(url,headers=headers,params=params).json()

        try:
            if len(response["data"])>0:
                return response["data"]

            else:
                return None

        except KeyError:
            raise twitchpy.errors.ClientError(response["message"])

    def create_entitlement_grants_upload_url(self,manifest_id,type):
        """
        Creates a URL where you can upload a manifest file and notify users that they have an entitlement

        Args:
            manifest_id (string): Unique identifier of the manifest file to be uploaded
                                  Must be 1-64 characters
            type (string): Type of entitlement being granted
                           Only bulk_drops_grant is supported

        Returns:
            str
        """

        url="https://api.twitch.tv/helix/entitlements/upload"
        headers={"Authorization":f"Bearer {self.__app_token}","Client-Id":self.client_id}
        payload={"manifest_id":manifest_id,"type":type}

        response=requests.post(url,headers=headers,json=payload).json()

        try:
            if len(response["data"][0])>0:
                return response["data"][0][url]

            else:
                return None

        except KeyError:
            raise twitchpy.errors.ClientError(response["message"])

    def get_code_status(self,code,user_id):
        """
        Gets the status of one or more provided codes

        Args:
            code (str): The code to get the status of
            user_id (int): ID of the user which is going to receive the entitlement associated with the code

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

    def get_drops_entitlements(self,id="",user_id="",game_id="",first=20):
        """
        Gets a list of entitlements for a given organization that have been granted to a game, user, or both

        Args:
            id (str, optional): ID of the entitlement
            user_id (str, optional): A Twitch User ID
            game_id (str, optional): A Twitch Game ID
            first (int, optional): Maximum number of entitlements to return
                                   Default: 20
                                   Max: 100

        Returns:
            list
        """
        
        url="https://api.twitch.tv/helix/entitlements/drops"
        headers={"Authorization":f"Bearer {self.__user_token}","Client-Id":self.client_id}
        params={}

        if id!="":
            params["id"]=id

        if user_id!="":
            params["user_id"]=user_id

        if game_id!="":
            params["game_id"]=game_id

        if first!=20:
            params["first"]=first

        response=requests.get(url,headers=headers,params=params).json()

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

        Args:
            code (str): The code to redeem
            user_id (int): ID of the user which is going to receive the entitlement

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

    def get_top_games(self,first=20):
        """
        Gets the most popular games

        Args:
            first (int, optional): Maximum number of objects to return
                                   Maximum: 100
                                   Default: 20

        Returns:
            list
        """

        url=f"https://api.twitch.tv/helix/games/top"
        headers={"Authorization": f"Bearer {self.__app_token}","Client-Id":self.client_id}

        if first!=20:
            params={"first":first}
            response=requests.get(url,headers=headers,params=params).json()

        else:
            response=requests.get(url,headers=headers).json()

        games=[]
        
        try:
            for game in response["data"]:
                games.append(self.get_game(id=game["id"])[0])

            return games

        except KeyError:
            raise twitchpy.errors.ClientError(response["message"])

    def get_game(self,id="",name=""):
        """
        Gets games by game ID or name
        For a query to be valid, name and/or id must be specified

        Args:
            id (str, optional): Game ID
            name (str, optional): Game name
                                  The name must be an exact match

        Returns:
            Game
        """

        url="https://api.twitch.tv/helix/games"
        headers={"Authorization": f"Bearer {self.__app_token}","Client-Id":self.client_id}
        params={}

        if id!="":
            params["id"]=id

        if name!="":
            params["name"]=name

        response=requests.get(url,headers=headers,params=params).json()

        try:
            if len(response["data"])>0:
                game=Game(response["data"][0]["id"],response["data"][0]["name"],response["data"][0]["box_art_url"])

                return game

            else:
                return None

        except KeyError:
            raise twitchpy.errors.ClientError(response["message"])

    def get_hype_train_events(self,broadcaster_id,first=1,id=""):
        """
        Gets the information of the most recent Hype Train of the given channel ID

        Args:
            broadcaster_id (str): User ID of the broadcaster
            first (int, optional): Maximum number of objects to return
                                   Maximum: 100
                                   Default: 1
            id (str, optional): The id of the wanted event

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

        response=requests.get(url,headers=headers,params=params).json()

        try:
            if len(response["data"])>0:
                return response["data"]

            else:
                return None

        except KeyError:
            raise twitchpy.errors.ClientError(response["message"])

    def check_automod_status(self,broadcaster_id,msg_id,msg_user,user_id):
        """
        Determines whether a string message meets the channel’s AutoMod requirements

        Args:
            broadcaster_id (str): User ID of the broadcaster
            msg_id (str, optional): Developer-generated identifier for mapping messages to results
            msg_user (str, optional): Message text
            user_id (str, optional): User ID of the sender

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

    def get_banned_events(self,broadcaster_id,user_id="",first=20):
        """
        Returns all user bans and un-bans in a channel

        Args:
            broadcaster_id (str): User ID of the broadcaster
            user_id (str, optional): Filters the results and only returns a status object for ban events that include users being banned or un-banned in the channel
            first (int, optional): Maximum number of objects to return
                                   Maximum: 100
                                   Default: 20

        Returns:
            list
        """

        url="https://api.twitch.tv/helix/moderation/banned/events"
        headers={"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id}
        params={"broadcaster_id":broadcaster_id}

        if user_id!="":
            params["user_id"]=user_id

        if first!=20:
            params["first"]=first

        response=requests.get(url,headers=headers,params=params).json()

        try:
            if len(response["data"])>0:
                return response["data"]

            else:
                return None

        except KeyError:
            raise twitchpy.errors.ClientError(response["message"])

    def get_banned_users(self,broadcaster_id,user_id="",first=20):
        """
        Returns all banned and timed-out users in a channel

        Args:
            broadcaster_id (str): User ID of the broadcaster
            user_id (str, optional): Filters the results and only returns a status object for users who are banned in the channel
            first (int, optional): Maximum number of objects to return
                                   Maximum: 100
                                   Default: 20

        Returns:
            list
        """

        url="https://api.twitch.tv/helix/moderation/banned"
        headers={"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id}
        params={"broadcaster_id":broadcaster_id}

        if user_id!="":
            params["user_id"]=user_id

        if first!=20:
            params["first"]=first

        response=requests.get(url,headers=headers,params=params).json()

        try:
            if len(response["data"])>0:
                return response["data"]

            else:
                return None

        except KeyError:
            raise twitchpy.errors.ClientError(response["message"])

    def get_moderators(self,broadcaster_id,user_id="",first=20):
        """
        Returns all moderators in a channel

        Args:
            broadcaster_id (str): User ID of the broadcaster
            user_id (str, optional): Filters the results and only returns a status object for users who are moderators in this channel
            first (int, optional): Maximum number of objects to return
                                   Maximum: 100
                                   Default: 20

        Returns:
            list
        """

        url="https://api.twitch.tv/helix/moderation/moderators"
        headers={"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id}
        params={"broadcaster_id":broadcaster_id}

        if user_id!="":
            params["user_id"]=user_id

        if first!=20:
            params["first"]=first

        response=requests.get(url,headers=headers,params=params).json()

        try:
            if len(response["data"])>0:
                users=[]

                for user in response["data"]:
                    users.append(self.get_user(id=user["user_id"]))

                return users

            else:
                return None

        except KeyError:
            raise twitchpy.errors.ClientError(response["message"])

    def get_moderator_events(self,broadcaster_id,user_id="",first=20):
        """
        Returns a list of moderators or users added and removed as moderators from a channel

        Args:
            broadcaster_id (str): User ID of the broadcaster
            user_id (str, optional): Filters the results and only returns a status object for users who have been added or removed as moderators in the channel
            first (int, optional): Maximum number of objects to return
                                   Maximum: 100
                                   Default: 20

        Returns:
            list
        """

        url="https://api.twitch.tv/helix/moderation/moderators/events"
        headers={"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id}
        params={"broadcaster_id":broadcaster_id}

        if user_id!="":
            params["user_id"]=user_id

        if first!=20:
            params["first"]=first

        response=requests.get(url,headers=headers,params=params).json()

        try:
            if len(response["data"])>0:
                return response["data"]

            else:
                return None

        except KeyError:
            raise twitchpy.errors.ClientError(response["message"])

    def search_categories(self,query,first=20):
        """
        Returns a list of games or categories that match the query via name either entirely or partially

        Args:
            query (str): url encoded search query
            first (int, optional): Maximum number of objects to return
                                   Maximum: 100
                                   Default: 20

        Returns:
            list
        """

        url="https://api.twitch.tv/helix/search/categories"
        headers={"Authorization": f"Bearer {self.__app_token}","Client-Id":self.client_id}
        params={"query":query}

        if first!=20:
            params["first"]=first

        response=requests.get(url,headers=headers,params=params).json()

        try:
            if len(response["data"])>0:
                games=[]

                for game in response["data"]:
                    games.append(self.get_game(id=game["id"]))

                return games

            else:
                return None

        except KeyError:
            raise twitchpy.errors.ClientError(response["message"])

    def search_channels(self,query,first=20,live_only=False):
        """
        Returns a list of channels that match the query via channel name or description either entirely or partially

        Args:
            query (str): url encoded search query
            first (int, optional): Maximum number of objects to return
                                   Maximum: 100
                                   Default: 20
            live_only (bool, optional): Filter results for live streams only
                                        Default: false

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

        response=requests.get(url,headers=headers,params=params).json()

        try:
            if len(response["data"])>0:
                channels=[]

                for channel in response["data"]:
                    channels.append(self.get_channel(channel["id"]))

                return channels

            else:
                return None

        except KeyError:
            raise twitchpy.errors.ClientError(response["message"])

    def get_stream_key(self,broadcaster_id):
        """
        Gets the channel stream key for a user

        Args:
            broadcaster_id (str): User ID of the broadcaster

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
                                   Maximum: 100
                                   Default: 20
            game_id (str, optional): Returns streams broadcasting a specified game ID
            language (str, optional): Stream language
            user_id (str, optional): Returns streams broadcast by one or more specified user IDs
            user_login (str, optional): Returns streams broadcast by one or more specified user login names

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

        response=requests.get(url,headers=headers,params=params).json()

        try:
            if len(response["data"])>0:
                streams=[]

                for stream in response["data"]:
                    streams.append(Stream(stream["id"],stream["user_id"],stream["user_name"],stream["game_id"],stream["type"],stream["title"],stream["viewer_count"],stream["started_at"],stream["language"],stream["thumbnail_url"],stream["tag_ids"]))

                return streams

            else:
                return None

        except KeyError:
            raise twitchpy.errors.ClientError(response["message"])

    def create_stream_marker(self,user_id,description=""):
        """
        Creates a marker in the stream of a user specified by user ID

        Args:
            user_id (str): ID of the broadcaster in whose live stream the marker is created
            description (str, optional): Description of or comments on the marker
                                         Max length is 140 characters

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

    def get_stream_markers(self,user_id,video_id,first=20):
        """
        Gets a list of markers for either a specified user’s most recent stream or a specified VOD/video (stream), ordered by recency
        Only one of user_id and video_id must be specified

        Args:
            user_id (str): ID of the broadcaster from whose stream markers are returned
            video_id (str): ID of the VOD/video whose stream markers are returned
            first (int, optional): Number of values to be returned when getting videos by user or game ID
                                   Limit: 100
                                   Default: 20

        Returns:
            list
        """

        url="https://api.twitch.tv/helix/streams/markers"
        headers={"Authorization": f"Bearer {self.__app_token}","Client-Id":self.client_id}
        params={"user_id":user_id,"video_id":video_id}

        if first!=20:
            params["first"]=first

        response=requests.get(url,headers=headers,params=params).json()

        try:
            if len(response["data"])>0:
                return response["data"]

            else:
                return None

        except KeyError:
            raise twitchpy.errors.ClientError(response["message"])

    def get_channel(self,broadcaster_id):
        """
        Gets a channel

        Args:
            broadcaster_id (str): ID of the channel to be updated

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
                channel=Channel(self.app_token,self.client_id,self.client_secret,self.get_user(id=channel["broadcaster_id"]).login,channel["game_name"],channel["broadcaster_language"],channel["title"])
                
                return channel

            else:
                return None

        except:
            raise twitchpy.errors.ClientError(response["message"])

    def modify_channel_information(self,broadcaster_id,game_id="",broadcaster_language="",title=""):
        """
        Modifies channel information
        game_id, broadcaster_language and title parameters are optional, but at least one parameter must be provided

        Args:
            broadcaster_id (str): ID of the channel to be updated
            game_id (str, optional): The current game ID being played on the channel
            broadcaster_language (str, optional): The language of the channel
            title (str, optional): The title of the stream
        """

        url="https://api.twitch.tv/helix/channels"
        headers={"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id,"Content-Type":"application/json"}
        data={"broadcaster_id":broadcaster_id}

        if (game_id!="" and broadcaster_language!="") or (game_id!="" and title!="") or (broadcaster_language!="" and title!=""):
            raise twitchpy.errors.FewArgumentsError("game_id, broadcaster_language or title must be provided")

        if game_id!="":
            data["game_id"]=game_id

        if broadcaster_language!="":
            data["broadcaster_language"]=broadcaster_language

        if title!="":
            data["title"]=title

        response=requests.patch(url,headers=headers,data=data)

    def get_broadcaster_subscriptions(self,broadcaster_id,user_id="",first=20):
        """
        Get all of a broadcaster’s subscriptions

        Args:
            broadcaster_id (str): User ID of the broadcaster
            user_id (str, optional): ID of account to get subscription status of
            first (int, optional): Maximum number of objects to return
                                   Maximum: 100
                                   Default: 20

        Returns:
            list
        """

        url="https://api.twitch.tv/helix/subscriptions"
        headers={"Authorization":f"Bearer {self.__user_token}","Client-Id":self.client_id}
        params={"broadcaster_id":broadcaster_id}

        if user_id!="":
            params["user_id"]=user_id

        if first!=20:
            params["first"]=first

        response=requests.get(url,headers=headers,params=params).json()

        try:
            if len(response["data"])>0:
                return response["data"]

            else:
                return None

        except KeyError:
            raise twitchpy.errors.ClientError(response["message"])

    def get_all_stream_tags(self,first=20,tag_id=""):
        """
        Gets the list of all stream tags defined by Twitch

        Args:
            first (int, optional): Maximum number of objects to return
                                   Maximum: 100
                                   Default: 20
            tag_id (str, optional): ID of a tag

        Returns:
            list
        """

        url="https://api.twitch.tv/helix/tags/streams"
        headers={"Authorization":f"Bearer {self.__app_token}","Client-Id":self.client_id}

        if first==20 and tag_id=="":
            response=requests.get(url,headers=headers).json()

        else:
            params={}

            if first!=20:
                params["first"]=first

            if tag_id!="":
                params["tag_id"]=tag_id

            response=requests.get(url,headers=headers,params=params).json()

        try:
            if len(response["data"])>0:
                return response["data"]

            else:
                return None

        except KeyError:
            raise twitchpy.errors.ClientError(response["message"])

    def get_stream_tags(self,broadcaster_id):
        """
        Gets the list of tags for a specified stream (channel)

        Args:
            broadcaster_id (str): ID of the stream thats tags are going to be fetched

        Returns:
            list
        """

        url="https://api.twitch.tv/helix/tags/streams"
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
        If no tag ids are provided, all tags are removed from the stream

        Args:
            broadcaster_id (str): ID of the stream for which tags are to be replaced
            tag_ids (list, optional): IDs of tags to be applied to the stream
                                      Maximum of 100 supported
        """

        url="https://api.twitch.tv/helix/streams/tags"
        headers={"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id,"Content-Type":"application/json"}
        data={"broadcaster_id":broadcaster_id}

        if len(tag_ids)>0:
            data["tag_ids"]=tag_ids

        response=requests.put(url,headers=headers,data=data)

    def create_user_follows(self,from_id,to_id,allow_notifications=False):
        """
        Adds a specified user to the followers of a specified channel

        Args:
            from_id (str): User ID of the follower
            to_id (str): ID of the channel to be followed by the user
            allow_notifications (bool, optional): If true, the user gets email or push notifications (depending on the user’s notification settings) when the channel goes live
                                                  Default value is false
        """

        url="https://api.twitch.tv/helix/users/follows"
        headers={"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id,"Content-Type":"application/json"}
        payload={"from_id":from_id,"to_id":to_id}

        if allow_notifications!=False:
            payload["allow_notifications"]=allow_notifications

        response=requests.post(url,headers=headers,json=payload)

    def delete_user_follows(self,from_id,to_id):
        """
        Deletes a specified user from the followers of a specified channel

        Args:
            from_id (str): User ID of the follower
            to_id (str): Channel to be unfollowed by the user
        """

        url="https://api.twitch.tv/helix/users/follows"
        headers={"Authorization": f"Bearer {self.__user_token}","Client-Id":self.client_id}
        data={"from_id":from_id,"to_id":to_id}

        response=requests.delete(url,headers=headers,data=data)

    def get_user(self,id="",login=""):
        """
        Gets an user

        Args:
            id (str, optional): User ID
            login (str, optional): User login name

        Returns:
            User
        """

        url="https://api.twitch.tv/helix/users"
        headers={"Authorization": f"Bearer {self.__app_token}","Client-Id":self.client_id}
        params={}

        if id!="":
            params["id"]=id

        if login!="":
            login=login.replace("@","").lower()
            params["login"]=login

        response=requests.get(url,headers=headers,params=params).json()

        try:
            if len(response["data"])>0:
                user=response["data"][0]
                user=User(user["id"],user["login"],user["display_name"],user["type"],user["broadcaster_type"],user["description"],user["profile_image_url"],user["offline_image_url"],user["view_count"])
                
                return user

            else:
                return None

        except KeyError:
            raise twitchpy.errors.ClientError(response["message"])

    def get_user_follows(self,first=20,from_id="",to_id=""):
        """
        Gets information on follow relationships between Twitch users
        At minimum, from_id or to_id must be provided for a query to be valid

        Args:
            first (int, optional): Maximum number of objects to return
                                   Maximum: 100
                                   Default: 20
            from_id (str, optional): User ID
            to_id (str, optional): User ID

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

        response=requests.get(url,headers=headers,params=params).json()

        try:
            if len(response["data"])>0:
                return response["data"]

            else:
                return None

        except KeyError:
            raise twitchpy.errors.ClientError(response["message"])

    def update_user(self,description=""):
        """
        Updates the description of a user

        Args:
            description (str, optional): User’s account description

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
                user=get_user(id=response["data"][0]["id"])

                return user

            else:
                return None

        except KeyError:
            raise twitchpy.errors.ClientError(response["message"])

    def get_user_extensions(self):
        """
        Gets a list of all extensions (both active and inactive) for a specified user

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
        Gets information about active extensions installed by a specified user

        Args:
            user_id (str, optional): ID of the user whose installed extensions will be returned

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
        Updates the activation state, extension ID, and/or version number of installed extensions for a specified user

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

    def get_videos(self,id,user_id,game_id,first=20,language="",period="all",sort="time",type="all"):
        """
        Gets video information by video ID, user ID, or game ID
        Each request must specify one video id, one user_id, or one game_id

        Args:
            id (str): ID of the video
            user_id (str): ID of the user who owns the video
            game_id (str): ID of the game the video is of
            first (int, optional): Number of values to be returned
                                   Limit: 100
                                   Default: 20
            language (str, optional): Language of the video
            period (str, optional): Period during which the video was created
                                    Valid values: "all", "day", "week", "month"
            sort (str, optional): Sort order of the videos
                                  Valid values: "time", "trending", "views"
                                  Default: "time"
            type (str, optional): Type of video
                                  Valid values: "all", "upload", "archive", "highlight"
                                  Default: "all"

        Returns:
            list
        """

        url="https://api.twitch.tv/helix/videos"
        headers={"Authorization": f"Bearer {self.__app_token}","Client-Id":self.client_id}
        params={"id":id,"user_id":user_id,"game_id":game_id}

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

        response=requests.get(url,headers=headers,params=params).json()

        try:
            if len(response["data"])>0:
                videos=[]

                for video in response["data"]:
                    videos.append(Video(video["id"],video["user_id"],video["user_name"],video["title"],video["description"],video["created_at"],video["published_at"],video["url"],video["thumbnail_url"],video["viewable"],video["view_count"],video["language"],video["type"],video["duration"]))

                return videos

            else:
                return None

        except KeyError:
            raise twitchpy.errors.ClientError(response["message"])

    def get_webhook_subscriptions(self,first=20):
        """
        Gets the Webhook subscriptions of a user

        Args:
            first (int, optional): Number of values to be returned per page
                                   Limit: 100
                                   Default: 20

        Returns:
            list
        """

        url="https://api.twitch.tv/helix/webhooks/subscriptions"
        headers={"Authorization": f"Bearer {self.__app_token}","Client-Id":self.client_id}

        if first==20:
            response=requests.get(url,headers=headers).json()

        else:
            params={"first":first}

            response=requests.get(url,headers=headers,params=params).json()

        try:
            if len(response["data"])>0:
                return response["data"]

            else:
                return None

        except KeyError:
            raise twitchpy.errors.ClientError(response["message"])

    def get_chatters(self,channel_name):
        """
        Gets all users in a chat

        Args:
            channel_name (str): Name of the user who is owner of the chat

        Returns:
            list
        """

        channel_name=channel_name.replace("@","").lower()

        url=f"https://tmi.twitch.tv/group/user/{channel_name}/chatters"
        headers={"Authorization": f"Bearer {self.__app_token}","Client-Id":self.client_id}

        response=requests.post(url,headers=headers).json()

        try:
            return response["chatters"]

        except KeyError:
            raise twitchpy.errors.ClientError(response["message"])