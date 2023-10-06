from twitchpy.channel import Channel
from twitchpy.charity_campaign import CharityCampaign
from twitchpy.charity_campaign_donation import CharityCampaignDonation
from twitchpy.client import Client
import ssl
import socket
from twitchpy.eventsub_subscription import EventSubSubscription
from twitchpy.game import Game
from twitchpy.hypetrain_event import HypeTrainEvent
from twitchpy.message import Message
from twitchpy.prediction import Prediction
from twitchpy.user import User

class Bot:
    """
    Represents a bot
    """

    def __init__(self,oauth_token,client_id,client_secret,redirect_uri,tokens_path,username,channels,command_prefix,code="",jwt_token="",ready_message=""):
        """
        Args:
            oauth_token (str): OAuth token
            client_id (str): Client ID
            client_secret (str): Client secret
            redirect_uri (str): Redirect URI
            tokens_path (str): Path of tokens file (file included)
            username (str): Name of the bot
            channels (list): Names of channels the bot will access
            command_prefix (str): Prefix of the commands the bot will recognize
            code (str, optional): Authorization code for getting an user token
            jwt_token (str, optional): JWT Token
            ready_message (str, optional): Message that the bot will send through the chats of the channels it access
        """

        self.__irc_server="irc.chat.twitch.tv"
        self.__irc_port=6697
        self.__client=Client(oauth_token,client_id,client_secret,redirect_uri,tokens_path,code,jwt_token)
        self.__oauth_token=oauth_token
        self.__finish=False
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

    def __send_command(self,command):
        if "PASS" not in command and "PONG" not in command:
            print(f"< {command}")

        self.irc.send((command+"\r\n").encode())

    def __send_privmsg(self,channel,text):
        self.__send_command(f"PRIVMSG #{channel} :{text}")

    def __login(self):
        self.__send_command(f"PASS {self.__oauth_token}")
        self.__send_command(f"NICK {self.username}")

    def __join(self,channel):
        self.__send_command(f"JOIN #{channel}")
        self.__send_privmsg(channel,self.ready_message)

    def __connect(self):
        self.irc=ssl.wrap_socket(socket.socket())
        self.irc.settimeout(1)
        self.irc.connect((self.__irc_server,self.__irc_port))

        self.__login()

        for channel in self.channels:
            self.__join(channel)

    def run(self):
        """
        Runs the bot
        """

        self.__connect()
        self.__loop()

    def stop(self):
        """
        Stops the bot
        """

        self.__finish=True

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

        text_start=next((idx for idx,part in enumerate(parts) if part.startswith(":")),None)

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

        hash_start=next((idx for idx,part in enumerate(irc_args) if part.startswith("#")),None)

        if hash_start is not None:
            channel=irc_args[hash_start][1:]

        message=Message(prefix=prefix,user=user,channel=channel,irc_command=irc_command,irc_args=irc_args,text=text,text_command=text_command,text_args=text_args)

        return message

    def __execute_listeners(self, message: Message) -> None:
        for listener in self.custom_listeners.values():
            listener(message)

    def __remove_listeners(self) -> None:
        for listener in self.listeners_to_remove:
            if listener in self.custom_listeners.keys():
                self.custom_listeners.pop(listener)

        self.listeners_to_remove=[]

    def __execute_methods_before_commands(self, message: Message) -> None:
        for before in self.custom_methods_before_commands.values():
            before(message)

    def __remove_methods_before_commands(self) -> None:
        for method in self.methods_before_commands_to_remove:
            if method in self.custom_methods_before_commands.keys():
                self.custom_methods_before_commands.pop(method)

    def __execute_commands(self, message: Message) -> None:
        self.custom_commands[message.text_command](message)
        self.__remove_methods_after_commands()

    def __execute_methods_after_commands(self, message: Message) -> None:
        for after in self.custom_methods_after_commands.values():
            after(message)

    def __remove_methods_after_commands(self) -> None:
        for method in self.methods_after_commands_to_remove:
            if method in self.custom_methods_after_commands.keys():
                self.custom_methods_after_commands.pop(method)

    def __handle_message(self, received_msg):
        if len(received_msg) == 0:
            return

        message = self.__parse_message(received_msg)
        print(f"[{message.channel}] {message.user}: {message.text}")

        if message.irc_command == "PING":
            self.__send_command("PONG :tmi.twitch.tv")

        else:
            self.__execute_listeners(message)
            self.__remove_listeners()

            if message.irc_command == "PRIVMSG":
                if message.text_command in self.custom_commands:
                    self.__execute_methods_before_commands(message)
                    self.__remove_methods_before_commands()
                    self.__execute_commands(message)
                    self.__execute_methods_after_commands(message)
                    self.__remove_methods_after_commands()

    def __loop(self):
        while not self.__finish:
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
        Adds a listener to the bot
        Listeners work only when a message is received
        Listeners must receive as a parameter the last message in the chat

        Args:
            name (str): Command's name
            listener (str): Method that will be executed when the command is invoked
        """

        self.custom_listeners[name]=listener

    def add_command(self,name,command):
        """
        Adds a command to the bot
        Commands must receive as a parameter the messages which call them

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
            dict
        """

        return self.__client.start_commercial(broadcaster_id,length)

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

        Returns:
            list
        """

        return self.__client.get_extension_analytics(ended_at,extension_id,first,started_at,type)

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

        Returns:
            list
        """

        return self.__client.get_game_analytics(ended_at,first,game_id,started_at,type)

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

        Returns:
            list
        """

        return self.__client.get_bits_leaderboard(count,period,started_at,user_id)

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

        Returns:
            list
        """

        return self.__client.get_extension_transactions(extension_id,id,first)

    def get_channel(self, broadcaster_id: str | list[str]) -> Channel:
        """
        Gets a channel

        Args:
            broadcaster_id (str | list[str]): ID of the channel to be updated
                Maximum: 100

        Returns:
            Channel
        """

        return self.__client.get_channel(broadcaster_id)

    def modify_channel_information(self, broadcaster_id: str, game_id: str = "", broadcaster_language: str = "", title: str = "", delay: int = 0, tags: list[str] = []):
        """
        Updates a channel’s properties

        Args:
            broadcaster_id (str): The ID of the broadcaster whose channel you want to update
                ID must match the user ID in the user access token
            game_id (str): The ID of the game that the user plays
            broadcaster_language (str): The user’s preferred language
                Set the value to an ISO 639-1 two-letter language code
                Set to “other” if the user’s preferred language is not a Twitch supported language
            title (str): The title of the user’s stream
            delay (int): The number of seconds you want your broadcast buffered before streaming it live
                Only users with Partner status may set this field
                Maximum: 900 seconds
            tags (list[str]): A list of channel-defined tags to apply to the channel
                Maximum: 10
        """

        self.__client.modify_channel_information(broadcaster_id, game_id, broadcaster_language, title, delay, tags)

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
            Reward
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

    def get_custom_reward(self,broadcaster_id,id=[],only_manageable_rewards=False):
        """
        Returns a list of Custom Reward objects for the Custom Rewards on a channel

        Args:
            broadcaster_id (str): Provided broadcaster_id must match the user_id in the user OAuth token
            id (list, optional): This parameter filters the results and only returns reward objects for the Custom Rewards with matching ID
                                Maximum: 50
            only_manageable_rewards (bool, optional): When set to true, only returns custom rewards that the calling broadcaster can manage
                                                      Default: false

        Returns:
            list
        """

        return self.__client.get_custom_reward(broadcaster_id,id,only_manageable_rewards)

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
            Reward
        """

        return self.__client.update_custom_reward(broadcaster_id,id,title,prompt,cost,background_color,is_enabled,is_user_input_required,is_max_per_stream_enabled,max_per_stream,is_max_per_user_per_stream_enabled,max_per_user_per_stream,is_global_cooldown_enabled,global_cooldown_seconds,is_paused,should_redemptions_skip_request_queue)

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

        Returns:
            Redemption
        """

        return self.__client.update_redemption_status(id,broadcaster_id,reward_id,status)

    def get_charity_campaign(self, broadcaster_id: str) -> CharityCampaign:
        """
        Gets information about the charity campaign that a broadcaster is running

        Args:
            broadcaster_id (str): The ID of the broadcaster that’s currently running a charity campaign
                This ID must match the user ID in the access token

        Returns:
            CharityCampaign
        """

        return self.__client.get_charity_campaign(broadcaster_id)

    def get_charity_campaign_donations(self, broadcaster_id: str, first: int = 20) -> list[CharityCampaignDonation]:
        """
        Gets the list of donations that users have made to the broadcaster’s active charity campaign

        Args:
            broadcaster_id (str): The ID of the broadcaster that’s currently running a charity campaign
                This ID must match the user ID in the access token
            first (int): The maximum number of items to return
                Default: 20
                Minimum: 1

        Returns:
            list[CharityCampaignDonation]
        """

        return self.__client.get_charity_campaign_donations(broadcaster_id, first)

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

        Returns:
            list[User]
        """

        return self.__client.get_chatters(broadcaster_id, moderator_id, first)

    def get_channel_emotes(self,broadcaster_id):
        """
        Gets all custom emotes for a specific Twitch channel including subscriber emotes, Bits tier emotes, and follower emotes
        Custom channel emotes are custom emoticons that viewers may use in Twitch chat once they are subscribed to, cheered in, or followed the channel that owns the emotes

        Args:
            broadcaster_id (str): The broadcaster whose emotes are being requested

        Returns:
            list
        """

        return self.__client.get_channel_emotes(broadcaster_id)

    def get_global_emotes(self):
        """
        Gets all global emotes
        Global emotes are Twitch-specific emoticons that every user can use in Twitch chat

        Returns:
            list
        """

        return self.__client.get_global_emotes()

    def get_emote_sets(self,emote_set_id):
        """
        Gets all Twitch emotes for one or more specific emote sets

        Args:
            emote_set_id (list): ID(s) of the emote set
                                 Maximum: 25

        Returns:
            list
        """

        return self.__client.get_emote_sets(emote_set_id)

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

    def get_chat_settings(self,broadcaster_id,moderator_id=""):
        """
        Gets the broadcaster’s chat settings

        Args:
            broadcaster_id (str): The ID of the broadcaster whose chat settings you want to get
            moderator_id (str, optional): Required only to access the non_moderator_chat_delay or non_moderator_chat_delay_duration settings
                                          The ID of a user that has permission to moderate the broadcaster’s chat room
                                          This ID must match the user ID associated with the user OAuth token
                                          If the broadcaster wants to get their own settings (instead of having the moderator do it), set this parameter to the broadcaster’s ID, too

        Returns:
            dict
        """

        return self.__client.get_chat_settings(broadcaster_id,moderator_id)

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

        Returns:
            dict
        """

        return self.__client.update_chat_settings(broadcaster_id,moderator_id,emote_mode,follower_mode,follower_mode_duration,non_moderator_chat_delay,non_moderator_chat_delay_duration,slow_mode,slow_mode_wait_time,subscriber_mode,unique_chat_mode)

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

        self.__client.send_chat_announcement(broadcaster_id, moderator_id, message, color)

    def send_a_shoutout(self, from_broadcaster_id: str, to_broadcaster_id: str, moderator_id: str) -> None:
        """
        Sends a Shoutout to the specified broadcaster

        Args:
            from_broadcaster_id (str): The ID of the broadcaster that’s sending the Shoutout
            to_broadcaster_id (str): The ID of the broadcaster that’s receiving the Shoutout
            moderator_id (str): The ID of the broadcaster or a user that is one of the broadcaster’s moderators
                This ID must match the user ID in the access token
        """

        self.__client.send_a_shoutout(from_broadcaster_id, to_broadcaster_id, moderator_id)

    def get_user_chat_color(self, user_id: str | list[str]) -> list[dict]:
        """
        Gets the color used for the user’s name in chat

        Args:
            user_id (str | list[str]): The ID of the user whose username color you want to get
                Maximum: 100

        Returns:
            list[dict]
        """

        return self.__client.get_user_chat_color(user_id)

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

        self.__client.update_user_chat_color(user_id, color)

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

        Returns:
            list
        """

        return self.__client.get_clips(broadcaster_id,game_id,id,ended_at,first,started_at)

    def get_code_status(self,code,user_id):
        """
        Gets the status of one or more provided codes
        All codes are single-use

        Args:
            code (list): The code to get the status of
                         Maximum: 20
            user_id (int): The user account which is going to receive the entitlement associated with the code

        Returns:
            list
        """

        return self.__client.get_code_status(code,user_id)

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

        Returns:
            list
        """

        return self.__client.get_drops_entitlements(id,user_id,game_id,fulfillment_status,first)

    def update_drops_entitlements(self,entitlement_ids=[],fulfillment_status=""):
        """
        Updates the fulfillment status on a set of Drops entitlements, specified by their entitlement IDs

        Args:
            entitlement_ids (list, optional): An array of unique identifiers of the entitlements to update
                                              Maximum: 100
            fulfillment_status (str, optional): A fulfillment status
                                                Valid values are "CLAIMED" or "FULFILLED"

        Returns:
            list
        """

        return self.__client.update_drops_entitlements(entitlement_ids,fulfillment_status)

    def redeem_code(self,code,user_id):
        """
        Redeems one or more provided codes
        All codes are single-use

        Args:
            code (list): The code to redeem to the authenticated user’s account
                         Maximum: 20
            user_id (int): The user account which is going to receive the entitlement associated with the code

        Returns:
            list
        """

        return self.__client.redeem_code(code,user_id)

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

        Returns:
            dict
        """

        return self.__client.get_extension_configuration_segment(broadcaster_id,extension_id,segment)

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

        self.__client.set_extension_configuration_segment(extension_id,segment,broadcaster_id,content,version)

    def set_extension_required_configuration(self,broadcaster_id,extension_id,extension_version,configuration_version):
        """
        Enable activation of a specified Extension, after any required broadcaster configuration is correct

        Args:
            broadcaster_id (str): User ID of the broadcaster who has activated the specified Extension on their channel
            extension_id (str): ID for the Extension to activate
            extension_version (str): The version fo the Extension to release
            configuration_version (str): The version of the configuration to use with the Extension
        """

        self.__client.set_extension_required_configuration(broadcaster_id,extension_id,extension_version,configuration_version)

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

        self.__client.send_extension_pubsub_message(target,broadcaster_id,is_global_broadcast,message)

    def get_extension_live_channels(self,extension_id,first=20):
        """
        Returns one page of live channels that have installed or activated a specific Extension, identified by a client ID value assigned to the Extension when it is created
        A channel that recently went live may take a few minutes to appear in this list, and a channel may continue to appear on this list for a few minutes after it stops broadcasting

        Args:
            extension_id (str): ID of the Extension to search for
            first (int, optional): Maximum number of objects to return
                                   Default: 20

        Returns:
            list
        """

        return self.__client.get_extension_live_channels(extension_id,first)

    def get_extension_secrets(self):
        """
        Retrieves a specified Extension’s secret data consisting of a version and an array of secret objects
        Each secret object contains a base64-encoded secret, a UTC timestamp when the secret becomes active, and a timestamp when the secret expires

        Returns:
            list
        """

        return self.__client.get_extension_secrets()

    def create_extension_secret(self,delay=300):
        """
        Creates a JWT signing secret for a specific Extension
        Also rotates any current secrets out of service, with enough time for instances of the Extension to gracefully switch over to the new secret

        Args:
            delay (int, optional): JWT signing activation delay for the newly created secret in seconds
                                   Minimum: 300
                                   Default: 300

        Returns:
            list
        """

        return self.__client.create_extension_secret(delay)

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

        self.__client.send_extension_chat_message(broadcaster_id,text,extension_id,extension_version)

    def get_extensions(self,extension_id,extension_version=""):
        """
        Gets information about your Extensions; either the current version or a specified version

        Args:
            extension_id (str): ID of the Extension
            extension_version (str, optional): The specific version of the Extension to return
                                               If not provided, the current version is returned

        Returns:
            list
        """

        return self.__client.get_extensions(extension_id,extension_version)

    def get_released_extensions(self,extension_id,extension_version=""):
        """
        Gets information about a released Extension; either the current version or a specified version

        Args:
            extension_id (str): ID of the Extension
            extension_version (str, optional): The specific version of the Extension to return
                                               If not provided, the current version is returned

        Returns:
            dict
        """

        return self.__client.get_released_extensions(extension_id,extension_version)

    def get_extension_bits_products(self,extension_client_id,should_include_all=False):
        """
        Gets a list of Bits products that belongs to an Extension

        Args:
            extension_client_id (str): Extension client ID
            should_include_all (bool, optional): Whether Bits products that are disabled/expired should be included in the response
                                                 Default: false

        Returns:
            list
        """

        return self.__client.get_extension_bits_products(extension_client_id,should_include_all)

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
            is_broadcast (bool, optional): Indicates if Bits product purchase events are broadcast to all instances of an Extension on a channel via the “onTransactionComplete” helper callback.
                                           Default: false

        Returns:
            dict
        """

        return self.__client.update_extension_bits_product(extension_client_id, sku, cost, display_name, in_development, expiration, is_broadcast)

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

        Returns:
            EventSubSubscription
        """

        return self.__client.create_eventsub_subscription(type,version,condition,transport)

    def delete_eventsub_subscription(self,id):
        """
        Delete an EventSub subscription

        Args:
            id (str): The subscription ID for the subscription to delete
        """

        self.__client.delete_eventsub_subscription(id)

    def get_eventsub_subscriptions(self, status: str = "", type: str = "", user_id: str = "") -> list[EventSubSubscription]:
        """
        Get a list of your EventSub subscriptions
        Only include one filter query parameter

        Args:
            status (str, optional): Filters subscriptions by one status type
                Valid values: "enabled", "webhook_callback_verification_pending", "webhook_callback_verification_failed", "notification_failures_exceeded", "authorization_revoked", "moderator_removed", "user_removed", "version_removed", "websocket_disconnected", "websocket_failed_ping_pong", "websocket_received_inbound_traffic", "websocket_connection_unused", "websocket_internal_error", "websocket_network_timeout", "websocket_network_error"
            type (str, optional): Filters subscriptions by subscription type name
            user_id (str, optional): Filter subscriptions by user ID

        Returns:
            list[EventSubSubscription]
        """

        return self.__client.get_eventsub_subscriptions(status, type, user_id)

    def get_top_games(self,first=20):
        """
        Gets games sorted by number of current viewers on Twitch, most popular first

        Args:
            first (int, optional): Maximum number of objects to return
                                   Default: 20

        Returns:
            list
        """

        return self.__client.get_top_games(first)

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

        Returns:
            list[Game]
        """

        return self.__client.get_games(id, name, igdb_id)

    def get_creator_goals(self,broadcaster_id):
        """
        Gets the broadcaster’s list of active goals
        Use this to get the current progress of each goal

        Args:
            broadcaster_id (str): The ID of the broadcaster that created the goals

        Returns:
            list
        """

        return self.__client.get_creator_goals(broadcaster_id)

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

        Returns:
            list[HypeTrainEvent]
        """

        return self.__client.get_hype_train_events(broadcaster_id, first)

    def check_automod_status(self, broadcaster_id: str, msg_id: str, msg_user: str) -> list[dict]:
        """
        Determines whether a string message meets the channel’s AutoMod requirements

        Args:
            broadcaster_id (str): Provided broadcaster_id must match the user_id in the auth token
            msg_id (str): Developer-generated identifier for mapping messages to results
            msg_user (str): Message text

        Returns:
            list[dict]
        """

        return self.__client.check_automod_status(broadcaster_id, msg_id, msg_user)

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

        self.__client.manage_held_automod_messages(user_id,msg_id,action)

    def get_automod_settings(self,broadcaster_id,moderator_id):
        """
        Gets the broadcaster’s AutoMod settings, which are used to automatically block inappropriate or harassing messages from appearing in the broadcaster’s chat room

        Args:
            broadcaster_id (str): The ID of the broadcaster whose AutoMod settings you want to get
            moderator_id (str): The ID of a user that has permission to moderate the broadcaster’s chat room
                                This ID must match the user ID associated with the user OAuth token
                                If the broadcaster wants to get their own AutoMod settings (instead of having the moderator do it), set this parameter to the broadcaster’s ID, too

        Returns:
            dict
        """
        
        return self.__client.get_automod_settings(broadcaster_id,moderator_id)

    def update_automod_settings(self,broadcaster_id,moderator_id,aggression=0,bullying=0,disability=0,misogyny=0,overall_level=0,race_ethnicity_or_religion=0,sex_based_terms=0,sexuality_sex_or_gender=0,swearing=0):
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

        Returns:
            dict
        """

        return self.__client.update_automod_settings(broadcaster_id,moderator_id,aggression,bullying,disability,misogyny,overall_level,race_ethnicity_or_religion,sex_based_terms,sexuality_sex_or_gender,swearing)

    def get_banned_users(self,broadcaster_id,user_id=[],first=20):
        """
        Returns all banned and timed-out users in a channel

        Args:
            broadcaster_id (str): Provided broadcaster_id must match the user_id in the auth token
            user_id (list, optional): Filters the results and only returns a status object for users who are banned in this channel and have a matching user_id
                                     Maximum: 100
            first (int, optional): Maximum number of objects to return
                                   Default: 20

        Returns:
            list
        """

        return self.__client.get_banned_users(broadcaster_id,user_id,first)

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

        Returns:
            dict
        """

        return self.__client.ban_user(broadcaster_id,moderator_id,reason,user_id,duration)

    def unban_user(self,broadcaster_id,moderator_id,user_id):
        """
        Removes the ban or timeout that was placed on the specified user

        Args:
            broadcaster_id (str): The ID of the broadcaster whose chat room the user is banned from chatting in
            moderator_id (str): The ID of a user that has permission to moderate the broadcaster’s chat room
                                This ID must match the user ID associated with the user OAuth token
                                If the broadcaster wants to remove the ban (instead of having the moderator do it), set this parameter to the broadcaster’s ID, too
            user_id (str): The ID of the user to remove the ban or timeout from
        """

        self.__client.unban_user(broadcaster_id,moderator_id,user_id)

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

        Returns:
            list
        """

        return self.__client.get_blocked_terms(broadcaster_id,moderator_id,first)

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

        Returns:
            dict
        """

        return self.__client.add_blocked_term(broadcaster_id,moderator_id,text)

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

        self.__client.remove_blocked_term(broadcaster_id,id,moderator_id)

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

        self.__client.delete_chat_messages(broadcaster_id, moderator_id, message_id)

    def get_moderators(self,broadcaster_id,user_id=[],first=20):
        """
        Returns all moderators in a channel

        Args:
            broadcaster_id (str): Provided broadcaster_id must match the user_id in the auth token
            user_id (list, optional): Filters the results and only returns a status object for users who are moderators in this channel and have a matching user_id
                                      Maximum: 100
            first (int, optional): Maximum number of objects to return
                                   Default: 20

        Returns:
            list
        """

        return self.__client.get_moderators(broadcaster_id,user_id,first)

    def add_channel_moderator(self, broadcaster_id: str, user_id: str) -> None:
        """
        Adds a moderator to the broadcaster’s chat room

        Args:
            broadcaster_id (str): The ID of the broadcaster that owns the chat room
                This ID must match the user ID in the access token
            user_id (str): The ID of the user to add as a moderator in the broadcaster’s chat room
        """

        self.__client.add_channel_moderator(broadcaster_id, user_id)

    def remove_channel_moderator(self, broadcaster_id: str, user_id: str) -> None:
        """
        Removes a moderator from the broadcaster’s chat room

        Args:
            broadcaster_id (str): The ID of the broadcaster that owns the chat room
                This ID must match the user ID in the access token
            user_id (str): The ID of the user to remove as a moderator from the broadcaster’s chat room
        """

        self.__client.remove_channel_moderator(broadcaster_id, user_id)

    def get_vips(self, broadcaster_id: str, user_id: list[str] = [], first: int = 20) -> list[User]:
        """
        Gets a list of the broadcaster’s VIPs

        Args:
            broadcaster_id (str): The ID of the broadcaster whose list of VIPs you want to get
                This ID must match the user ID in the access token
            user_id (list[str]): Filters the list for specific VIPs
                Maximum: 100
            first (int): The number of items to return
                Default: 20
                Minimum: 1
                Maximum: 100

        Returns:
            list[User]
        """

        return self.__client.get_vips(broadcaster_id, user_id, first)

    def add_channel_vip(self, user_id: str, broadcaster_id: str) -> None:
        """
        Adds the specified user as a VIP in the broadcaster’s channel

        Args:
            user_id (str): The ID of the user to give VIP status to
            broadcaster_id (str): The ID of the broadcaster that’s adding the user as a VIP
                This ID must match the user ID in the access token
        """

        self.__client.add_channel_vip(user_id, broadcaster_id)

    def remove_channel_vip(self, user_id: str, broadcaster_id: str) -> None:
        """
        Removes the specified user as a VIP in the broadcaster’s channel

        Args:
            user_id (str): The ID of the user to remove VIP status from
            broadcaster_id (str): The ID of the user to remove VIP status from
        """

        self.__client.remove_channel_vip(user_id, broadcaster_id)

    def update_shield_mode_status(self, broadcaster_id: str, moderator_id: str, is_active: bool) -> dict:
        """
        Activates or deactivates the broadcaster’s Shield Mode

        Args:
            broadcaster_id (str): The ID of the broadcaster whose Shield Mode you want to activate or deactivate
            moderator_id (str): The ID of the broadcaster or a user that is one of the broadcaster’s moderators
                This ID must match the user ID in the access token
            is_active (bool): A Boolean value that determines whether to activate Shield Mode

        Returns:
            dict
        """

        return self.__client.update_shield_mode_status(broadcaster_id, moderator_id, is_active)

    def get_shield_mode_status(self, broadcaster_id: str, moderator_id: str) -> dict:
        """
        Gets the broadcaster’s Shield Mode activation status

        Args:
            broadcaster_id (str): The ID of the broadcaster whose Shield Mode activation status you want to get
            moderator_id (str): The ID of the broadcaster or a user that is one of the broadcaster’s moderators
                This ID must match the user ID in the access token

        Returns:
            dict
        """

        return self.__client.get_shield_mode_status(broadcaster_id, moderator_id)

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

        Returns:
            list
        """
        
        return self.__client.get_polls(broadcaster_id,id,first)

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

        Returns:
            Poll
        """

        return self.__client.create_poll(broadcaster_id, title, choices, duration, channel_points_voting_enabled, channel_points_per_vote)

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

        Returns:
            list
        """

        return self.__client.get_predictions(broadcaster_id,id,first)

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

        Returns:
            Prediction
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
            Prediction
        """

        return self.__client.end_prediction(broadcaster_id,id,status,winning_outcome_id)

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

        return self.__client.start_raid(from_broadcaster_id, to_broadcaster_id)

    def cancel_raid(self, broadcaster_id: str) -> None:
        """
        Cancel a pending raid
        
        Args:
            broadcaster_id (str): The ID of the broadcaster that initiated the raid
                This ID must match the user ID in the user access token
        """

        self.__client.cancel_raid(broadcaster_id)

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

        Returns:
            list
        """

        return self.__client.get_channel_stream_schedule(broadcaster_id,id,start_time,utc_offset,first)

    def get_channel_icalendar(self, broadcaster_id):
        """
        Gets all scheduled broadcasts from a channel’s stream schedule as an iCalendar

        Args:
            broadcaster_id (str): User ID of the broadcaster who owns the channel streaming schedule

        Returns:
            str
        """

        return self.__client.get_channel_icalendar(broadcaster_id)

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
        """

        self.__client.update_channel_stream_schedule(broadcaster_id,is_vacation_enabled,vacation_start_time,vacation_end_time,timezone)

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

        Returns:
            StreamSchedule
        """

        return self.__client.create_channel_stream_schedule_segment(broadcaster_id,start_time,timezone,is_recurring,duration,category_id,title)

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

        Returns:
            StreamSchedule
        """

        return self.__client.update_channel_stream_schedule_segment(broadcaster_id,id,start_time,duration,category_id,title,is_canceled,timezone)

    def delete_channel_stream_schedule_segment(self,broadcaster_id,id):
        """
        Delete a single scheduled broadcast or a recurring scheduled broadcast for a channel’s stream schedule

        Args:
            broadcaster_id (str): User ID of the broadcaster who owns the channel streaming schedule
                                  Provided broadcaster_id must match the user_id in the user OAuth token
            id (str): The ID of the streaming segment to delete
        """

        self.__client.delete_channel_stream_schedule_segment(broadcaster_id,id)

    def search_categories(self,query,first=20):
        """
        Returns a list of games or categories that match the query via name either entirely or partially

        Args:
            query (str): URI encoded search query
            first (int, optional): Maximum number of objects to return
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
                                   Default: 20
            live_only (bool, optional): Filter results for live streams only
                                        Default: false

        Returns:
            list
        """

        return self.__client.search_channels(query,first,live_only)

    def get_soundtrack_current_track(self,broadcaster_id):
        """
        Gets the Soundtrack track that the broadcaster is playing

        Args:
            broadcaster_id (str): The ID of the broadcaster that’s playing a Soundtrack track

        Returns:
            SoundtrackTrack
        """

        return self.__client.get_soundtrack_current_track(broadcaster_id)

    def get_soundtrack_playlist(self,id):
        """
        Gets a Soundtrack playlist, which includes its list of tracks

        Args:
            id (str): The ID of the Soundtrack playlist to get

        Returns:
            SoundtrackPlaylist
        """

        return self.__client.get_soundtrack_playlist(id)

    def get_soundtrack_playlists(self):
        """
        Gets a list of Soundtrack playlists

        Returns:
            list
        """

        return self.__client.get_soundtrack_playlists()

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

        Returns:
            list
        """

        return self.__client.get_stream_markers(user_id,video_id,first)

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

    def get_all_stream_tags(self,first=20,tag_id=[]):
        """
        Gets the list of all stream tags defined by Twitch

        Args:
            first (int, optional): Maximum number of objects to return
                                   Default: 20
            tag_id (list, optional): ID of a tag

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

    def get_teams(self,name="",id=""):
        """
        Gets information for a specific Twitch Team
        One of the two optional query parameters must be specified to return Team information

        Args:
            name (str, optional): Team name
            id (str, optional): Team ID

        Returns:
            Team
        """

        return self.__client.get_teams(name,id)

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

        Returns:
            list
        """

        return self.__client.get_users(id,login)

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
                                   Default: 20
            from_id (str, optional): User ID
                                     The request returns information about users who are being followed by the from_id user
            to_id (str, optional): User ID
                                   The request returns information about users who are following the to_id user

        Returns:
            list
        """

        return self.__client.get_user_follows(first,from_id,to_id)

    def get_user_block_list(self,broadcaster_id,first=20):
        """
        Gets a specified user’s block list

        Args:
            broadcaster_id (str): User ID for a Twitch user
            first (int, optional): Maximum number of objects to return
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

        Returns:
            list
        """

        return self.__client.get_videos(id,user_id,game_id,first,language,period,sort,type)

    def delete_video(self,id):
        """
        Deletes a video
        Videos are past broadcasts, Highlights, or uploads

        Args:
            id (str): ID of the video(s) to be deleted
                      Limit: 5
        """

        self.__client.delete_video(id)

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

        self.__client.send_whisper(from_user_id, to_user_id, message)

    def get_webhook_subscriptions(self,first=20):
        """
        Gets the Webhook subscriptions of an application identified by a Bearer token, in order of expiration

        Args:
            first (int, optional): Number of values to be returned
                                   Default: 20

        Returns:
            list
        """

        return self.__client.get_webhook_subscriptions(first)

    def send(self,channel,text):
        """
        Sends a message by chat

        Args:
            channel (str): Owner of the chat
            text (str): Message's text
        """

        self.__send_privmsg(channel,text)

    def ban(self,channel,user,reason=""):
        """
        Bans a user

        Args:
            channel (str): Channel who bans
            username (str): User to ban
            reason (str, optional): Reason of the ban
        """

        self.__send_privmsg(channel,f"/ban @{user} {reason}")

    def unban(self,channel,user):
        """
        Undoes the ban of a user

        Args:
            channel (str): Name of the channel who readmits
            user (str): Name of the user to readmit
        """

        self.__send_privmsg(channel,f"/unban @{user}")

    def clear(self,channel):
        """
        Clears the chat

        Args:
            channel (str): Channel to clean the chat
        """

        self.__send_privmsg(channel,"/clear")

    def delete_poll(self,channel):
        """
        Eliminates the active poll

        Args:
            channel (str): Channel in which eliminate the poll
        """
        
        self.__send_privmsg(channel,"/deletepoll")

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

        self.__send_privmsg(channel,"/emoteonlyoff")

    def endpoll(self,channel):
        """
        Finish the active poll

        Args:
            channel (str): Channel in which finish the poll
        """

        self.__send_privmsg(channel,"/endpoll")

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

    def unhost(self,channel):
        """
        Unhosts the hosted channel

        Args:
            channel (str): Channel who unhosts
        """

        self.__send_privmsg(channel,f"/unhost")

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

    def unmod(self,channel,username):
        """
        Removes the moderator's rank from a user

        Args:
            channel (str): Channel who removes the moderator's rank
            username (str): User's name
        """

        self.__send_privmsg(channel,f"/unmod {username}")

    def poll(self,channel):
        """
        Opens a configuration menu for creating a poll

        Args:
            channel (str): Channel in which create the poll
        """

        self.__send_privmsg(channel,"/poll")

    def prediction(self,channel):
        """
        Opens a configuration menu for creating a prediction

        Args:
            channel (str): Channel in which create the prediction
        """

        self.__send_privmsg(channel,"/prediction")

    def raid(self,channel,username):
        """
        Raids another channel

        Args:
            channel (str): Name of the channel who raids
            username (str): Name of the channel to raid
        """

        self.__send_privmsg(channel,f"/raid {username}")

    def unraid(self,channel):
        """
        Cancels an raid

        Args:
            channel (str): Channel who unraids
        """

        self.__send_privmsg(channel,"/unraid")

    def requests(self,channel):
        """
        Opens the reward requests queue

        Args:
            channel (str): Owner of the rewards
        """

        self.__send_privmsg(channel,"/requests")

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

    def untimeout(self,channel,username):
        """
        Cancels the timeout of a user

        Args:
            channel (str): Channel who ejected the user
            username (str): User to readmit
        """

        self.__send_privmsg(channel,f"/untimeout @{username}")

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

    def user(self,channel,username):
        """
        Shows information about a user

        Args:
            channel (str): Channel in which to show the user's information
            username (str): User to show information about
        """

        self.__send_privmsg(channel,f"/user {username}")

    def vip(self,channel,username):
        """
        Makes a user vip

        Args:
            channel (str): Channel who makes a user vip
            username (str): User's name
        """

        self.__send_privmsg(channel,f"/vip {username}")

    def unvip(self,channel,username):
        """
        Removes the vip range from a user

        Args:
            channel (str): Channel who remove's the vip range
            username (str): User's name
        """

        self.__send_privmsg(channel,f"/unvip {username}")

    def block(self,channel,user):
        """
        Blocks a user

        Args:
            channel (str): Channel who blocks
            username (str): User to block
        """

        self.__send_privmsg(channel,f"/block @{user}")

    def unblock(self,channel,user):
        """
        Unblocks a user

        Args:
            channel (str): Name of the channel who unblocks
            user (str): Name of the user to unblock
        """

        self.__send_privmsg(channel,f"/unblock @{user}")

    def color(self,channel,color):
        """
        Changes the color of the channel's name in the chat

        Args:
            channel (str): Channel to change color
            color (str): New color's name
        """

        self.__send_privmsg(channel,f"/color {color}")

    def help(self,channel,command):
        """
        Shows detailed information about a command

        Args:
            channel (str): Channel in which show the command's information
            command (str): Command to show information about
        """

        self.__send_privmsg(channel,f"/help {command}")

    def me(self,channel,text):
        """
        Sends a message by chat in italics

        Args:
            channel (str): Owner of the chat
            text (str): Message's text
        """

        self.__send_privmsg(channel,f"/me {text}")

    def mods(self,channel):
        """
        Shows the moderators list of a channel

        Args:
            channel (str): Channel who owns the moderators
        """

        self.__send_privmsg(channel,"/mods")

    def vips(self,channel):
        """
        Shows the vips list of a channel

        Args:
            channel (str): Channel who owns the vips
        """

        self.__send_privmsg(channel,"/vips")

    def vote(self,channel,index):
        """
        Votes in the active poll

        Args:
            channel (str): Owner of the poll
            index (int): Number of the option
        """

        self.__send_privmsg(channel,f"/vote {index}")

    def commercial(self,channel,duration=30):
        """
        Places advertising in the channel

        Args:
            channel (str): Channel on which start the commercial
            duration (int): Duration of advertising
        """

        self.__send_privmsg(channel,f"/commercial {duration}")

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

        self.commands_to_remove.append(name)

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