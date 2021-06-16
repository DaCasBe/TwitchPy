from twitchpy.client import Client
import ssl
import socket
from twitchpy.message import Message
from twitchpy.channel import Channel

class Bot:
    """
    Represents a bot
    """

    def __init__(self,oauth_token,client_id,client_secret,username,channels,command_prefix,code="",ready_message=""):
        """
        Args:
            oauth_token (str): OAuth token
            client_id (str): Client ID
            client_secret (str): Client secret
            username (str): Name of the bot
            channels (list): Names of channels the bot will access
            command_prefix (str): Prefix of the commands the bot will recognize
            code (str, optional): Authorization code
            ready_message (str, optional): Message that the bot will send through the chats of the channels it access
        """

        self.__irc_server="irc.chat.twitch.tv"
        self.__irc_port=6697
        self.__client=Client(oauth_token,client_id,client_secret,code)
        self.__oauth_token=oauth_token
        self.username=username

        self.channels=[]

        for channel in channels:
            self.channels.append(channel.replace("@","").lower())

        self.command_prefix=command_prefix
        self.ready_message=ready_message
        self.custom_checks={}
        self.custom_listeners={}
        self.listeners_to_remove=[]
        self.custom_commands={}
        self.commands_to_remove=[]
        self.custom_methods_after_commands={}
        self.methods_after_commands_to_remove=[]
        self.custom_methods_before_commands={}
        self.methods_before_commands_to_remove=[]

    def __send_privmsg(self,channel,text):
        self.__send_command(f"PRIVMSG #{channel} :{text}")

    def __send_command(self,command):
        if "PASS" not in command:
            print(f"< {command}")

        self.irc.send((command+"\r\n").encode())

    def run(self):
        """
        Runs the bot
        """

        self.irc=ssl.wrap_socket(socket.socket())
        self.irc.settimeout(1)
        self.irc.connect((self.__irc_server,self.__irc_port))
        
        self.__send_command(f"PASS {self.__oauth_token}")
        self.__send_command(f"NICK {self.username}")

        for channel in self.channels:
            self.__send_command(f"JOIN #{channel}")
            self.__send_privmsg(channel,self.ready_message)

        self.__loop()

    def __get_user_from_prefix(self,prefix):
        domain=prefix.split("!")[0]

        if domain.endswith(".tmi.twitch.tv"):
            return domain.replace(".tmi.twitch.tv","")

        if "tmi.twitch.tv" not in domain:
            return domain

        return None

    def __remove_prefix(self,string,prefix):
        if not string.startswith(prefix):
            return string

        return string[len(prefix):]

    def __parse_message(self,received_msg):
        parts=received_msg.split(" ")

        prefix=None
        user=None
        channel=None
        irc_command=None
        irc_args=None
        text=None
        text_command=None
        text_args=None

        if parts[0].startswith(":"):
            prefix=self.__remove_prefix(parts[0],":")
            user=self.__get_user_from_prefix(prefix)
            parts=parts[1:]

        text_start=next(
            (idx for idx,part in enumerate(parts) if part.startswith(":")),
            None
        )

        if text_start is not None:
            text_parts=parts[text_start:]
            text_parts[0]=text_parts[0][1:]
            text=" ".join(text_parts)

            if text_parts[0].startswith(self.command_prefix):
                text_command=self.__remove_prefix(text_parts[0],self.command_prefix)
                text_args=text_parts[1:]

            parts=parts[:text_start]

        irc_command=parts[0]
        irc_args=parts[1:]

        hash_start=next(
            (idx for idx,part in enumerate(irc_args) if part.startswith("#")),
            None
        )

        if hash_start is not None:
            channel=irc_args[hash_start][1:]

        message=Message(prefix=prefix,user=user,channel=channel,irc_command=irc_command,irc_args=irc_args,text=text,text_command=text_command,text_args=text_args)

        return message

    def __handle_message(self,received_msg):
        if len(received_msg)==0:
            return

        message=self.__parse_message(received_msg)
        print(f"[{message.channel}] {message.user}: {message.text}")

        if message.irc_command=="PING":
            self.__send_command("PONG :tmi.twitch.tv")

        for listener in self.custom_listeners.values():
            listener(message)

        for listener in self.listeners_to_remove:
            if listener in self.custom_listeners.keys():
                self.custom_listeners.pop(listener)

        self.listeners_to_remove=[]

        if message.irc_command=="PRIVMSG":
            if message.text_command in self.custom_commands:
                for before in self.custom_methods_before_commands.values():
                    before(message)

                for method in self.methods_before_commands_to_remove:
                    if method in self.custom_methods_before_commands.keys():
                        self.custom_methods_before_commands.pop(method)

                self.custom_commands[message.text_command](message)

                for after in self.custom_methods_after_commands.values():
                    after(message)

                for method in self.methods_after_commands_to_remove:
                    if method in self.custom_methods_after_commands.keys():
                        self.custom_methods_after_commands.pop(method)

    def __loop(self):
        while True:
            try:
                received_msgs=self.irc.recv(2048).decode()

                for received_msg in received_msgs.split("\r\n"):
                    self.__handle_message(received_msg)

                for command in self.commands_to_remove:
                    if command in self.custom_commands.keys():
                        self.custom_commands.pop(command)

            except socket.timeout:
                for check in self.custom_checks.values():
                    check()

    def add_check(self,name,check):
        """
        Adds a check to the bot
        Checks work permanently

        Args:
            name (str): Check's name
            check (func): Method that will act as a check
        """

        self.custom_checks[name]=check

    def add_listener(self,name,listener):
        """
        Adds a command to the bot
        Listeners work only when a message is received

        Args:
            name (str): Command's name
            listener (str): Method that will be executed when the command is invoked
        """

        self.custom_listeners[name]=listener

    def add_command(self,name,command):
        """
        Adds a command to the bot

        Args:
            name (str): Command's name
            command (func): Method that will be executed when the command is invoked
        """

        self.custom_commands[name]=command

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

        return self.__client.start_commercial(broadcaster_id,length)

    def get_extension_analytics(self,extension_id="",first=20,type=""):
        """
        Gets a URL that Extension developers can use to download analytics reports for their Extensions
        The URL is valid for 5 minutes

        Args:
            extension_id (str, optional): Client ID value assigned to the extension when it is created
            first (int, optional): Maximum number of objects to return
                                   Maximum: 100
                                   Default: 20
            type (str, optional): Type of analytics report that is returned
                                  Valid values: "overview_v2"

        Returns:
            list
        """

        return self.__client.get_extension_analytics(extension_id,first,type)

    def get_game_analytics(self,first=20,game_id="",type=""):
        """
        Gets a URL that game developers can use to download analytics reports for their games
        The URL is valid for 5 minutes

        Args:
            first (int, optional): Maximum number of objects to return
                                   Maximum: 100
                                   Default: 20
            game_id (str, optional): Game ID
            type (str, optional): Type of analytics report that is returned
                                  Valid values: "overview_v2"

        Returns:
            list
        """

        return self.__client.get_game_analytics(first,game_id,type)

    def get_bits_leaderboard(self,count=10,user_id=""):
        """
        Gets a ranked list of Bits leaderboard information for a broadcaster

        Args:
            count (int, optional): Number of results to be returned
                                   Maximum: 100
                                   Default: 10
            user_id (str, optional): ID of the user whose results are returned
                                     As long as count is greater than 1, the returned data includes additional users, with Bits amounts above and below the user specified

        Returns:
            list
        """

        return self.__client.get_bits_leaderboard(count,user_id)

    def get_cheermotes(self,broadcaster_id=""):
        """
        Retrieves the list of available Cheermotes
        Cheermotes returned are available throughout Twitch, in all Bits-enabled channels

        Args:
            broadcaster_id (str, optional): ID for the broadcaster who might own specialized Cheermotes

        Returns:
            list
        """

        return self.__client.get_cheermotes(broadcaster_id)

    def get_extension_transactions(self,extension_id,id="",first=20):
        """
        Allows extension back end servers to fetch a list of transactions that have occurred for their extension across all of Twitch
        A transaction is a record of a user exchanging Bits for an in-Extension digital good

        Args:
            extension_id (str): ID of the extension to list transactions for
            id (str, optional): Transaction IDs to look up
            first (int, optional): Maximum number of objects to return
                                   Maximum: 100
                                   Default: 20

        Returns:
            list
        """

        return self.__client.get_extension_transactions(extension_id,id,first)

    def get_channel(self,broadcaster_id):
        """
        Gets a channel

        Args:
            broadcaster_id (str): ID of the channel to be updated

        Returns:
            Channel
        """

        return self.__client.get_channel(broadcaster_id)

    def modify_channel_information(self,broadcaster_id,game_id="",broadcaster_language="",title=""):
        """
        Modifies channel information for users
        game_id, broadcaster_language and title parameters are optional, but at least one parameter must be provided

        Args:
            broadcaster_id (str): ID of the channel to be updated
            game_id (str, optional): The current game ID being played on the channel
            broadcaster_language (str, optional): The language of the channel
                                                  A language value must be either the ISO 639-1 two-letter code for a supported stream language or “other”
            title (str, optional): The title of the stream
        """

        self.__client.modify_channel_information(broadcaster_id,game_id,broadcaster_language,title)

    def get_channel_editors(self,broadcaster_id):
        """
        Gets a list of users who have editor permissions for a specific channel

        Args:
            broadcaster_id (str): Broadcaster’s user ID associated with the channel

        Returns:
            list
        """

        return self.__client.get_channel_editors(broadcaster_id)

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

        Returns:
            list
        """

        return self.__client.create_custom_reward(broadcaster_id,title,cost,prompt,is_enabled,background_color,is_user_input_required,is_max_per_stream_enabled,max_per_stream,is_max_per_user_per_stream_enabled,max_per_user_per_stream,is_global_cooldown_enabled,global_cooldown_seconds,should_redemptions_skip_request_queue)

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

        self.__client.delete_custom_reward(broadcaster_id,id)

    def get_custom_reward(self,broadcaster_id,id="",only_manageable_rewards=False):
        """
        Returns a list of Custom Reward objects for the Custom Rewards on a channel

        Args:
            broadcaster_id (str): Provided broadcaster_id must match the user_id in the user OAuth token
            id (str, optional): This parameter filters the results and only returns reward objects for the Custom Rewards with matching ID
            only_manageable_rewards (bool, optional): When set to true, only returns custom rewards that the calling broadcaster can manage
                                                      Default: false

        Returns:
            list
        """

        return self.__client.get_custom_reward(broadcaster_id,id,only_manageable_rewards)

    def get_custom_reward_redemption(self,broadcaster_id,reward_id,id="",status="",sort="OLDEST",first=20):
        """
        Returns Custom Reward Redemption objects for a Custom Reward on a channel that was created by the same client_id
        Developers only have access to get and update redemptions for the rewards created programmatically by the same client_id

        Args:
            broadcaster_id (str): Provided broadcaster_id must match the user_id in the user OAuth token
            reward_id (str): When ID is not provided, this parameter returns Custom Reward Redemption objects for redemptions of the Custom Reward with ID reward_id
            id (str, optional): When id is not provided, this param filters the results and only returns Custom Reward Redemption objects for the redemptions with matching ID
            status (str, optional): This param filters the Custom Reward Redemption objects for redemptions with the matching status
                                    Can be one of UNFULFILLED, FULFILLED or CANCELED
            sort (str, optional): Sort order of redemptions returned when getting the Custom Reward Redemption objects for a reward
                                  One of: OLDEST, NEWEST
                                  Default: OLDEST
            first (int, optional): Number of results to be returned when getting the Custom Reward Redemption objects for a reward
                                   Limit: 50
                                   Default: 20

        Returns:
            list
        """

        return self.__client.get_custom_reward_redemption(broadcaster_id,reward_id,id,status,sort,first)

    def update_custom_reward(self,broadcaster_id,id,title="",prompt="",cost=None,background_color="",is_enabled=None,is_user_input_required=None,is_max_per_stream_enabled=None,max_per_stream=None,is_max_per_user_per_stream_enabled=False,max_per_user_per_stream=None,is_global_cooldown_enabled=False,global_cooldown_seconds=None,is_paused=None,should_redemptions_skip_request_queue=None):
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

        Returns:
            list
        """

        return self.__client.update_custom_reward(broadcaster_id,id,title,prompt,cost,background_color,is_enabled,is_user_input_required,is_max_per_stream_enabled,max_per_stream,is_max_per_user_per_stream_enabled,max_per_user_per_stream,is_global_cooldown_enabled,global_cooldown_seconds,is_paused,should_redemptions_skip_request_queue)

    def update_redemption_status(self,id,broadcaster_id,reward_id,status=""):
        """
        Updates the status of Custom Reward Redemption objects on a channel that are in the UNFULFILLED status
        The Custom Reward Redemption specified by id must be for a Custom Reward created by the client_id attached to the user OAuth token

        Args:
            id (str): ID of the Custom Reward Redemption to update
                      Must match a Custom Reward Redemption on broadcaster_id’s channel
            broadcaster_id (str): Provided broadcaster_id must match the user_id in the user OAuth token
            reward_id (str): ID of the Custom Reward the redemptions to be updated are for
            status (str, optional): The new status to set redemptions to
                                    Can be either FULFILLED or CANCELED
                                    Updating to CANCELED will refund the user their Channel Points

        Returns:
            list
        """

        return self.__client.update_redemption_status(id,broadcaster_id,reward_id,status)

    def get_channel_chat_badges(self,broadcaster_id):
        """
        Gets a list of custom chat badges that can be used in chat for the specified channel
        This includes subscriber badges and Bit badges

        Args:
            broadcaster_id (str): The broadcaster whose chat badges are being requested
                                  Provided broadcaster_id must match the user_id in the user OAuth token

        Returns:
            list
        """

        return self.__client.get_channel_chat_badges(broadcaster_id)

    def get_global_chat_badges(self):
        """
        Gets a list of chat badges that can be used in chat for any channel

        Returns:
            list
        """

        return self.__client.get_global_chat_badges()

    def create_clip(self,broadcaster_id,has_delay=False):
        """
        This returns both an ID and an edit URL for a new clip

        Args:
            broadcaster_id (str): ID of the stream from which the clip will be made
            has_delay (bool, optional): If false, the clip is captured from the live stream when the API is called; otherwise, a delay is added before the clip is captured (to account for the brief delay between the broadcaster’s stream and the viewer’s experience of that stream)
                                        Default: false

        Returns:
            dict
        """

        return self.__client.create_clip(broadcaster_id,has_delay)

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

        return self.__client.get_clips(broadcaster_id,game_id,id,first)

    def get_code_status(self,code,user_id):
        """
        Gets the status of one or more provided codes
        All codes are single-use

        Args:
            code (str): The code to get the status of
            user_id (int): The user account which is going to receive the entitlement associated with the code

        Returns:
            list
        """

        return self.__client.get_code_status(code,user_id)

    def get_drops_entitlements(self,id="",user_id="",game_id="",first=20):
        """
        Gets a list of entitlements for a given organization that have been granted to a game, user, or both

        Args:
            id (str, optional): ID of the entitlement
            user_id (str, optional): A Twitch User ID
            game_id (str, optional): A Twitch Game ID
            first (int, optional): Maximum number of entitlements to return
                                   Default: 20
                                   Max: 1000

        Returns:
            list
        """

        return self.__client.get_drops_entitlements(id,user_id,game_id,first)

    def redeem_code(self,code,user_id):
        """
        Redeems one or more provided codes
        All codes are single-use

        Args:
            code (str): The code to redeem to the authenticated user’s account
            user_id (int): The user account which is going to receive the entitlement associated with the code

        Returns:
            list
        """

        return self.__client.redeem_code(code,user_id)

    def create_eventsub_subscription(self,type,version,condition,transport):
        """
        Creates an EventSub subscription

        Args:
            type (str): The category of the subscription that is being created
                        Valid values: "channel.update", "channel.follow", "channel.subscribe", "channel.subscription.end", "channel.subscription.gift", "channel.cheer", "channel.raid", "channel.ban", "channel.unban", "channel.moderator.add", "channel.moderator.remove", "channel.channel_points_custom_reward.add", "channel.channel_points_custom_reward.update", "channel.channel_points_custom_reward.remove", "channel.channel_points_custom_reward_redemption.add", "channel.channel_points_custom_reward_redemption.update", "channel.poll.begin", "channel.poll.progress", "channel.poll.end", "channel.prediction.begin", "channel.prediction.progress", "channel.prediction.lock", "channel.prediction.end", "extension.bits_transaction.create", "channel.hype_train.begin", "channel.hype_train.progress", "channel.hype_train.end", "stream.online", "stream.offline", "user.authorization.revoke", "user.update"
            version (str): The version of the subscription type that is being created
                           Each subscription type has independent versioning
            condition (dict): Custom parameters for the subscription
            transport (dict): Notification delivery specific configuration including a method string
                              Valid transport methods include: webhook
                              In addition to the method string, a webhook transport must include the callback and secret information

        Returns:
            dict
        """

        return self.__client.create_eventsub_subscription(type,version,condition,transport)

    def delete_eventsub_subscription(self,id):
        """
        Delete an EventSub subscription

        Args:
            id (str): The subscription ID for the subscription to delete
        """

        self.__client.delete_eventsub_subscription(id)

    def get_eventsub_subscriptions(self,status="",type=""):
        """
        Get a list of your EventSub subscriptions
        Only include one filter query parameter

        Args:
            status (str, optional): Filters subscriptions by one status type
                                    Valid values: "enabled", "webhook_callback_verification_pending", "webhook_callback_verification_failed", "notification_failures_exceeded", "authorization_revoked", "user_removed"
            type (str, optional): Filters subscriptions by subscription type name

        Returns:
            list
        """

        return self.__client.get_eventsub_subscriptions(status,type)

    def get_top_games(self,first=20):
        """
        Gets games sorted by number of current viewers on Twitch, most popular first

        Args:
            first (int, optional): Maximum number of objects to return
                                   Maximum: 100
                                   Default: 20

        Returns:
            list
        """

        return self.__client.get_top_games(first)

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

        return self.__client.get_game(id,name)

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
                                   Maximum: 100
                                   Default: 1
            id (str, optional): The id of the wanted event

        Returns:
            list
        """

        return self.__client.get_hype_train_events(broadcaster_id,first,id)

    def check_automod_status(self,broadcaster_id,msg_id="",msg_user="",user_id=""):
        """
        Determines whether a string message meets the channel’s AutoMod requirements

        Args:
            broadcaster_id (str): Provided broadcaster_id must match the user_id in the auth token
            msg_id (str, optional): Developer-generated identifier for mapping messages to results
            msg_user (str, optional): Message text
            user_id (str, optional): User ID of the sender

        Returns:
            list
        """

        return self.__client.check_automod_status(broadcaster_id,msg_id,msg_user,user_id)

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

        self.manage_held_automod_messages(user_id,msg_id,action)

    def get_banned_events(self,broadcaster_id,user_id="",first=20):
        """
        Returns all user bans and un-bans in a channel

        Args:
            broadcaster_id (str): Provided broadcaster_id must match the user_id in the auth token
            user_id (str, optional): Filters the results and only returns a status object for ban events that include users being banned or un-banned in this channel and have a matching user_id
            first (int, optional): Maximum number of objects to return
                                   Maximum: 100
                                   Default: 20

        Returns:
            list
        """

        return self.__client.get_banned_events(broadcaster_id,user_id,first)

    def get_banned_users(self,broadcaster_id,user_id="",first=20):
        """
        Returns all banned and timed-out users in a channel

        Args:
            broadcaster_id (str): Provided broadcaster_id must match the user_id in the auth token
            user_id (str, optional): Filters the results and only returns a status object for users who are banned in this channel and have a matching user_id
            first (int, optional): Maximum number of objects to return
                                   Maximum: 100
                                   Default: 20

        Returns:
            list
        """

        return self.__client.get_banned_users(broadcaster_id,user_id,first)

    def get_moderators(self,broadcaster_id,user_id="",first=20):
        """
        Returns all moderators in a channel

        Args:
            broadcaster_id (str): Provided broadcaster_id must match the user_id in the auth token
            user_id (str, optional): Filters the results and only returns a status object for users who are moderators in this channel and have a matching user_id
            first (int, optional): Maximum number of objects to return
                                   Maximum: 100
                                   Default: 20

        Returns:
            list
        """

        return self.__client.get_moderators(broadcaster_id,user_id,first)

    def get_moderator_events(self,broadcaster_id,user_id="",first=20):
        """
        Returns a list of moderators or users added and removed as moderators from a channel

        Args:
            broadcaster_id (str): Provided broadcaster_id must match the user_id in the auth token
            user_id (str, optional): Filters the results and only returns a status object for users who have been added or removed as moderators in this channel and have a matching user_id
            first (int, optional): Maximum number of objects to return
                                   Maximum: 100
                                   Default: 20

        Returns:
            list
        """

        return self.__client.get_moderator_events(broadcaster_id,user_id,first)

    def get_polls(self,broadcaster_id,id="",first=20):
        """
        Get information about all polls or specific polls for a Twitch channel
        Poll information is available for 90 days

        Args:
            broadcaster_id (str): The broadcaster running polls
                                  Provided broadcaster_id must match the user_id in the user OAuth token
            id (str, optional): ID of a poll
            first (int, optional): Maximum number of objects to return
                                   Maximum: 20
                                   Default: 20

        Returns:
            list
        """
        
        return self.__client.get_polls(broadcaster_id,id,first)

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

        Returns:
            dict
        """

        return self.__client.create_poll(broadcaster_id,title,choices,duration,bits_voting_enabled,bits_per_vote,channel_points_voting_enabled,channel_points_per_vote)

    def end_poll(self,broadcaster_id,id,status):
        """
        End a poll that is currently active

        Args:
            broadcaster_id (str): The broadcaster running polls
                                  Provided broadcaster_id must match the user_id in the user OAuth token
            id (str): ID of the poll
            status (str): The poll status to be set
                          Valid values: "TERMINATED", "ARCHIVED"

        Returns:
            dict
        """

        return self.__client.end_poll(broadcaster_id,id,status)

    def get_predictions(self,broadcaster_id,id="",first=20):
        """
        Get information about all Channel Points Predictions or specific Channel Points Predictions for a Twitch channel

        Args:
            broadcaster_id (str): The broadcaster running Predictions
                                  Provided broadcaster_id must match the user_id in the user OAuth token
            id (str, optional): ID of a Prediction
            first (int, optional): Maximum number of objects to return
                                   Maximum: 20
                                   Default: 20

        Returns:
            list
        """

        return self.__client.get_predictions(broadcaster_id,id,first)

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

        Returns:
            dict
        """

        return self.__client.create_prediction(broadcaster_id,title,outcomes,prediction_window)

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

        Returns:
            dict
        """

        return self.__client.end_prediction(broadcaster_id,id,status,winning_outcome_id)

    def search_categories(self,query,first=20):
        """
        Returns a list of games or categories that match the query via name either entirely or partially

        Args:
            query (str): URI encoded search query
            first (int, optional): Maximum number of objects to return
                                   Maximum: 100
                                   Default: 20

        Returns:
            list
        """

        return self.__client.search_categories(query,first)

    def search_channels(self,query,first=20,live_only=False):
        """
        Returns a list of channels (users who have streamed within the past 6 months) that match the query via channel name or description either entirely or partially

        Args:
            query (str): URI encoded search query
            first (int, optional): Maximum number of objects to return
                                   Maximum: 100
                                   Default: 20
            live_only (bool, optional): Filter results for live streams only
                                        Default: false

        Returns:
            list
        """

        return self.__client.search_channels(query,first,live_only)

    def get_stream_key(self,broadcaster_id):
        """
        Gets the channel stream key for a user

        Args:
            broadcaster_id (str): User ID of the broadcaster

        Returns:
            str
        """

        return self.__client.get_stream_key(broadcaster_id)

    def get_streams(self,first=20,game_id="",language="",user_id="",user_login=""):
        """
        Gets active streams

        Args:
            first (int, optional): Maximum number of objects to return
                                   Maximum: 100
                                   Default: 20
            game_id (str, optional): Returns streams broadcasting a specified game ID
            language (str, optional): Stream language
                                      A language value must be either the ISO 639-1 two-letter code for a supported stream language or "other"
            user_id (str, optional): Returns streams broadcast by a specified user ID
            user_login (str, optional): Returns streams broadcast by a specified user login name

        Returns:
            list
        """

        return self.__client.get_streams(first,game_id,language,user_id,user_login)

    def get_followed_streams(self,user_id,first=100):
        """
        Gets information about active streams belonging to channels that the authenticated user follows

        Args:
            user_id (str): Results will only include active streams from the channels that this Twitch user follows
                           user_id must match the User ID in the bearer token
            first (int, optional): Maximum number of objects to return
                                   Maximum: 100
                                   Default: 100

        Returns:
            list
        """

        return self.__client.get_followed_streams(user_id,first)

    def create_stream_marker(self,user_id,description=""):
        """
        Creates a marker in the stream of a user specified by user ID
        A marker is an arbitrary point in a stream that the broadcaster wants to mark; e.g., to easily return to later
        The marker is created at the current timestamp in the live broadcast when the request is processed

        Args:
            user_id (str): ID of the broadcaster in whose live stream the marker is created
            description (str, optional): Description of or comments on the marker
                                         Max length is 140 characters

        Returns:
            list
        """

        return self.__client.create_stream_marker(user_id,description)

    def get_stream_markers(self,user_id,video_id,first=20):
        """
        Gets a list of markers for either a specified user’s most recent stream or a specified VOD/video (stream)
        A marker is an arbitrary point in a stream that the broadcaster wants to mark; e.g., to easily return to later
        The only markers returned are those created by the user identified by the Bearer token
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

        return self.__client.get_stream_markers(user_id,video_id,first)

    def get_broadcaster_subscriptions(self,broadcaster_id,user_id="",first=20):
        """
        Get all of a broadcaster’s subscriptions

        Args:
            broadcaster_id (str): User ID of the broadcaster
                                  Must match the User ID in the Bearer token
            user_id (str, optional): Filters results to only include potential subscriptions made by the provided user ID
            first (int, optional): Maximum number of objects to return
                                   Maximum: 100
                                   Default: 20

        Returns:
            list
        """

        return self.__client.get_broadcaster_subscriptions(broadcaster_id,user_id,first)

    def check_user_subscription(self,broadcaster_id,user_id):
        """
        Checks if a specific user (user_id) is subscribed to a specific channel (broadcaster_id)

        Args:
            broadcaster_id (str): User ID of an Affiliate or Partner broadcaster
            user_id (str): User ID of a Twitch viewer

        Returns:
            dict
        """

        return self.__client.check_user_subscription(broadcaster_id,user_id)

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

        return self.__client.get_all_stream_tags(first,tag_id)

    def get_stream_tags(self,broadcaster_id):
        """
        Gets the list of current stream tags that have been set for a channel

        Args:
            broadcaster_id (str): User ID of the channel to get tags

        Returns:
            list
        """

        return self.__client.get_stream_tags(broadcaster_id)

    def replace_stream_tags(self,broadcaster_id,tag_ids=[]):
        """
        Applies specified tags to a specified stream (channel), overwriting any existing tags applied to that stream
        If no tags are specified, all tags previously applied to the stream are removed
        Automated tags are not affected by this operation

        Args:
            broadcaster_id (str): ID of the stream for which tags are to be replaced
            tag_ids (list, optional): IDs of tags to be applied to the stream
        """

        self.__client.replace_stream_tags(broadcaster_id,tag_ids)

    def get_channel_teams(self,broadcaster_id):
        """
        Retrieves a list of Twitch Teams of which the specified channel/broadcaster is a member

        Args:
            broadcaster_id (str): User ID for a Twitch user

        Returns:
            list
        """

        return self.__client.get_channel_teams(broadcaster_id)

    def get_team(self,name="",id=""):
        """
        Gets information for a specific Twitch Team
        One of the two optional query parameters must be specified to return Team information

        Args:
            name (str, optional): Team name
            id (str, optional): Team ID

        Returns:
            Team
        """

        return self.__client.get_team(name,id)

    def get_user(self,id="",login=""):
        """
        Gets an user
        Users are identified by optional user IDs and/or login name
        If neither a user ID nor a login name is specified, the user is looked up by Bearer token

        Args:
            id (str, optional): User ID
            login (str, optional): User login name

        Returns:
            User
        """

        return self.__client.get_user(id,login)

    def update_user(self,description=""):
        """
        Updates the description of a user specified by the bearer token
        If the description parameter is not provided, no update will occur and the current user data is returned

        Args:
            description (str, optional): User’s account description

        Returns:
            User
        """

        return self.__client.update_user(description)

    def get_user_follows(self,first=20,from_id="",to_id=""):
        """
        Gets information on follow relationships between two Twitch users
        At minimum, from_id or to_id must be provided for a query to be valid

        Args:
            first (int, optional): Maximum number of objects to return
                                   Maximum: 100
                                   Default: 20
            from_id (str, optional): User ID
                                     The request returns information about users who are being followed by the from_id user
            to_id (str, optional): User ID
                                   The request returns information about users who are following the to_id user

        Returns:
            list
        """

        return self.__client.get_user_follows(first,from_id,to_id)

    def create_user_follows(self,from_id,to_id,allow_notifications=False):
        """
        Adds a specified user to the followers of a specified channel

        Args:
            from_id (str): User ID of the follower
            to_id (str): ID of the channel to be followed by the user
            allow_notifications (bool, optional): If true, the user gets email or push notifications (depending on the user’s notification settings) when the channel goes live
                                                  Default value is false
        """

        self.__client.create_user_follows(from_id,to_id,allow_notifications)

    def delete_user_follows(self,from_id,to_id):
        """
        Deletes a specified user from the followers of a specified channel

        Args:
            from_id (str): User ID of the follower
            to_id (str): Channel to be unfollowed by the user
        """

        self.__client.delete_user_follows(from_id,to_id)

    def get_user_block_list(self,broadcaster_id,first=100):
        """
        Gets a specified user’s block list

        Args:
            broadcaster_id (str): User ID for a Twitch user
            first (int, optional): Maximum number of objects to return
                                   Maximum: 100
                                   Default: 20

        Returns:
            list
        """

        return self.__client.get_user_block_list(broadcaster_id,first)

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

        self.__client.block_user(target_user_id,source_context,reason)

    def unblock_user(self,target_user_id):
        """
        Unblocks the specified user on behalf of the authenticated user

        Args:
            target_user_id (str): User ID of the user to be unblocked
        """

        self.__client.unblock_user(target_user_id)

    def get_user_extensions(self):
        """
        Gets a list of all extensions (both active and inactive) for a specified user, identified by a Bearer token

        Returns:
            list
        """

        return self.__client.get_user_extensions()

    def get_user_active_extensions(self,user_id=""):
        """
        Gets information about active extensions installed by a specified user, identified by a user ID or Bearer token

        Args:
            user_id (str, optional): ID of the user whose installed extensions will be returned

        Returns:
            list
        """

        return self.__client.get_user_active_extensions(user_id)

    def update_user_extensions(self):
        """
        Updates the activation state, extension ID, and/or version number of installed extensions for a specified user, identified by a Bearer token
        If you try to activate a given extension under multiple extension types, the last write wins (and there is no guarantee of write order)

        Returns:
            list
        """

        return self.__client.update_user_extensions()

    def get_videos(self,id,user_id,game_id,first=20,language="",period="all",sort="time",type="all"):
        """
        Gets video information by video ID, user ID, or game ID
        Each request must specify one video id, one user_id, or one game_id

        Args:
            id (str): ID of the video being queried
            user_id (str): ID of the user who owns the video
            game_id (str): ID of the game the video is of
            first (int, optional): Number of values to be returned when getting videos by user or game ID
                                   Limit: 100
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

        Returns:
            list
        """

        return self.__client.get_videos(id,user_id,game_id,first,language,period,sort,type)

    def delete_video(self,id):
        """
        Deletes a video
        Videos are past broadcasts, Highlights, or uploads

        Args:
            id (str): ID of the video to be deleted
        """

        self.__client.delete_videos(id)

    def get_webhook_subscriptions(self,first=20):
        """
        Gets the Webhook subscriptions of an application identified by a Bearer token, in order of expiration

        Args:
            first (int, optional): Number of values to be returned
                                   Limit: 100
                                   Default: 20

        Returns:
            list
        """

        return self.__client.get_webhook_subscriptions(first)

    def get_chatters(self,username):
        """
        Gets all users in a chat

        Args:
            channel_name (str): Name of the user who is owner of the chat

        Returns:
            dict
        """
        
        return self.__client.get_chatters(username)

    def ban(self,channel,user,reason=""):
        """
        Bans a user

        Args:
            channel (str): Channel who bans
            username (str): User to ban
            reason (str, optional): Reason of the ban
        """

        self.__send_privmsg(channel,f"/ban @{user} {reason}")

    def block(self,channel,user):
        """
        Blocks a user

        Args:
            channel (str): Channel who blocks
            username (str): User to block
        """

        self.__send_privmsg(channel,f"/block @{user}")

    def clear(self,channel):
        """
        Clears the chat

        Args:
            channel (str): Channel to clean the chat
        """

        self.__send_privmsg(channel,"/clear")

    def color(self,channel,color):
        """
        Changes the color of the channel's name in the chat

        Args:
            channel (str): Channel to change color
            color (str): New color's name
        """

        self.__send_privmsg(channel,f"/color {color}")

    def commercial(self,channel,duration=30):
        """
        Places advertising in the channel

        Args:
            channel (str): Channel on which start the commercial
            duration (int): Duration of advertising
        """

        self.__send_privmsg(channel,f"/commercial {duration}")

    def emoteonly(self,channel):
        """
        Activates the "emotes only" mode

        Args:
            channel (str): Channel on which activate the mode
        """

        self.__send_privmsg(channel,"/emoteonly")

    def emoteonly_off(self,channel):
        """
        Disables "emotes only" mode

        Args:
            channel (str): Channel on which disable the mode
        """

        self.__send_privmsg(self.name,"/emoteonlyoff")

    def followers(self,channel):
        """
        Activates the "followers only" mode

        Args:
            channel (str): Channel on which activate the mode
        """

        self.__send_privmsg(channel,"/followers")

    def followers_off(self,channel):
        """
        Disables the "followers only" mode

        Args:
            channel (str): Channel on which disable the mode
        """

        self.__send_privmsg(channel,"/followersoff")

    def host(self,channel,username):
        """
        Hosts a channel

        Args:
            channel (str): Name of the channel who hosts
            username (str): Name of the channel to host
        """

        self.__send_privmsg(channel,f"/host {username}")

    def marker(self,channel,description=""):
        """
        Leaves a mark on the channel's stream

        Args:
            channel (str): Channel in which leave the mark
            description (str): Mark's description
        """

        self.__send_privmsg(channel,f"/marker {description}")

    def mod(self,channel,username):
        """
        Makes a user mod

        Args:
            channel (str): Channel who promotes the user
            username (str): Name of the user to be promoted
        """

        self.__send_privmsg(channel,f"/mod {username}")

    def raid(self,channel,username):
        """
        Raids another channel

        Args:
            channel (str): Name of the channel who raids
            username (str): Name of the channel to raid
        """

        self.__send_privmsg(channel,f"/raid {username}")

    def send(self,channel,text):
        """
        Sends a message by chat

        Args:
            channel (str): Owner of the chat
            text (str): Message's text
        """

        self.__send_privmsg(channel,text)

    def send_me(self,channel,text):
        """
        Sends a message by chat in italics

        Args:
            channel (str): Owner of the chat
            text (str): Message's text
        """

        self.__send_privmsg(channel,f"/me {text}")

    def slow(self,channel,duration):
        """
        Activates the "slow" mode

        Args:
            channel (str): Channel on which activate the mode
            duration (int): Time between messages
        """

        self.__send_privmsg(channel,f"/slow {duration}")

    def slow_off(self,channel):
        """
        Disables the "slow" mode

        Args:
            channel (str): Channel on which disable the mode
        """

        self.__send_privmsg(channel,f"/slow_off")

    def subscribers(self,channel):
        """
        Activates the "subscribers only" mode

        Args:
            channel (str): Channel on which activate the mode
        """

        self.__send_privmsg(channel,"/subscribers")

    def subscribers_off(self,channel):
        """
        Disables "subscriber only" mode

        Args:
            channel (str): Channel on which disable the mode
        """

        self.__send_privmsg(channel,"/subscribersoff")

    def timeout(self,channel,user,duration=600,reason=""):
        """
        Expels a user temporarily

        Args:
            channel (str): Channel who ejects
            user (str): Name of the user to expel
            duration (int): Ejecting time
            reason (str): Reason for expulsion
        """

        self.__send_privmsg(channel,f"/timeout @{user} {duration} {reason}")

    def unban(self,channel,user):
        """
        Undoes the ban of a user

        Args:
            channel (str): Name of the channel who readmits
            user (str): Name of the user to readmit
        """

        self.__send_privmsg(channel,f"/unban @{user}")

    def unblock(self,channel,user):
        """
        Unblocks a user

        Args:
            channel (str): Name of the channel who unblocks
            user (str): Name of the user to unblock
        """

        self.__send_privmsg(channel,f"/unblock @{user}")

    def uniquechat(self,channel):
        """
        Activates the "unique" mode

        Args:
            channel (str): Channel on which activate the mode
        """

        self.__send_privmsg(channel,"/uniquechat")

    def uniquechat_off(self,channel):
        """
        Disables the "unique" mode

        Args:
            channel (str): Channel on which disable the mode
        """

        self.__send_privmsg(channel,"/uniquechatoff")

    def unhost(self,channel):
        """
        Unhosts the hosted channel

        Args:
            channel (str): Channel who unhosts
        """

        self.__send_privmsg(channel,f"/unhost")

    def unmod(self,channel,username):
        """
        Removes the moderator's rank from a user

        Args:
            channel (str): Channel who removes the moderator's rank
            username (str): User's name
        """

        self.__send_privmsg(channel,f"/unmod {username}")

    def unraid(self,channel):
        """
        Cancels an raid

        Args:
            channel (str): Channel who unraids
        """

        self.__send_privmsg(channel,f"/unraid")

    def unvip(self,channel,username):
        """
        Removes the vip range from a user

        Args:
            channel (str): Channel who remove's the vip range
            username (str): User's name
        """

        self.__send_privmsg(channel,f"/unvip {username}")

    def vip(self,channel,username):
        """
        Makes a user vip

        Args:
            channel (str): Channel who makes a user vip
            username (str): User's name
        """

        self.__send_privmsg(channel,f"/vip {username}")

    def whisper(self,channel,user,text):
        """
        Whispers to a user

        Args:
            channel (str): Channel on which send the whisp
            user (str): User's name
            text (str): Whisper's text
        """

        self.__send_privmsg(channel,f"/w {user} {text}")

    def add_method_after_commands(self,name,method):
        """
        Adds to the bot a method that will be executed after each command

        Args:
            name (str): Method's name
            method (func): Method to be executed after each command
        """

        self.custom_methods_after_commands[name]=method

    def add_method_before_commands(self,name,method):
        """
        Adds to the bot a method that will be executed before each command

        Args:
            name (str): Method's name
            method (func): Method to be executed before each command
        """

        self.custom_methods_before_commands[name]=method

    def remove_check(self,name):
        """
        Removes a check from the bot

        Args:
            name (str): Check's name
        """

        self.custom_checks.pop(name)

    def remove_listener(self,name):
        """
        Removes a listener from the bot

        Args:
            name (str): Listener's name
        """

        self.listeners_to_remove.append(name)

    def remove_command(self,name):
        """
        Removes a command from the bot

        Args:
            name (str): Command's name
        """

    def remove_method_after_commands(self,name):
        """
        Removes a method that is executed after each command

        Args:
            name (str): Method's name
        """

        self.custom_methods_after_commands.pop(name,None)

    def remove_method_before_commands(self,name):
        """
        Removes a method that is executed before each command

        Args:
            name (str): Method's name
        """

        self.custom_methods_before_commands.pop(name,None)