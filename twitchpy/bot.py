from twitchpy.client import Client
import ssl
import socket
from twitchpy.message import Message
from twitchpy.channel import Channel

class Bot:
    """
    Class that represents a bot
    """

    def __init__(self,oauth_token,client_id,client_secret,username,channels,command_prefix,ready_message=""):
        """
        Parameters:
        oauth_token (str) -- OAuth token to identify the application
        client_id (str) -- Client ID to identify the application
        client_secret (str) -- Client secret to identify the application
        username (str) -- Name of the bot
        channels (list[str]) -- Names of channels the bot will access
        command_prefix (str) -- Prefix of the commands the bot will recognize
        ready_message (str) -- Message that the bot will send through the chats of the channels it access
        """

        self.__irc_server="irc.chat.twitch.tv"
        self.__irc_port=6697
        self.__client=Client(oauth_token,client_id,client_secret)
        self.__oauth_token=oauth_token
        self.username=username
        self.channels=channels
        self.command_prefix=command_prefix
        self.ready_message=ready_message
        self.custom_checks={}
        self.custom_listeners={}
        self.custom_commands={}
        self.custom_methods_after_commands={}
        self.custom_methods_before_commands={}

    def __send_privmsg(self,channel,text):
        self.__send_command(f"PRIVMSG #{channel} :{text}")

    def __send_command(self,command):
        if "PASS" not in command:
            print(f"< {command}")

        self.irc.send((command+"\r\n").encode())

    def run(self):
        """
        Method for starting the bot
        """

        self.irc=ssl.wrap_socket(socket.socket())
        self.irc.connect((self.__irc_server,self.__irc_port))
        
        self.__send_command(f"PASS {self.__oauth_token}")
        self.__send_command(f"NICK {self.username}")

        for channel in self.channels:
            self.__send_command(f"JOIN #{channel}")
            self.__send_privmsg(channel,self.ready_message)

        for check in self.custom_checks.values():
            if check()!=True:
                return

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

        if message.irc_command=="PRIVMSG":
            if message.text_command in self.custom_commands:
                for before in self.custom_methods_before_commands.values():
                    before(message)

                self.custom_commands[message.text_command](message)

                for after in self.custom_methods_after_commands.values():
                    after(message)

    def __loop(self):
        while True:
            received_msgs=self.irc.recv(2048).decode()

            for received_msg in received_msgs.split("\r\n"):
                self.__handle_message(received_msg)

    def add_check(self,name,check):
        """
        Method for adding a check to the bot

        Checks are boolean methods that, if they don't return a False value, will prevent the bot from running

        Parameters:
        name (str) -- Check's name
        check (func) -- Method that will act as a check
        """

        self.custom_checks[name]=check

    def add_listener(self,name,listener):
        """
        Method for adding a listener to the bot

        Listeners are methods that continuously wait for a certain event to occur in order to execute an action

        Parameters:
        name (str) -- Listener's name
        listener (func) -- Method that will act as a listener
        """

        self.custom_listeners[name]=listener

    def add_command(self,name,command):
        """
        Method for adding a command to the bot

        Commands are methods that are executed when someone invokes them in a chat

        Parameters:
        name (str) -- Command's name
        command (func) -- Method that will be executed when the command is invoked
        """

        self.custom_commands[name]=command

    def get_channel(self,id):
        """
        Method that returns a channel

        Parameters:
        id (int) -- Channel's ID

        Return:
        Channel -- If the channel exists
        None -- If the channel doesn't exist
        """

        return self.__client.get_channel(id)

    def get_chatters(self,username):
        """
        Method for getting users into a channel chat

        Parameters:
        channel_name (str) -- Channel's name

        Return:
        dict
        """
        
        return self.__client.get_chatters(username)

    def get_follow(self,from_id,to_id):
        """
        Method for obtaining the date when one user followed another

        Parameters:
        from_id (int) -- ID of the user who is following
        to_id (int) -- ID of the user being followed

        Return:
        str -- If the first user follows the second one
        None -- If the first user does not follow the second one
        """

        return self.__client.get_follow(from_id,to_id)

    def get_followers(self,user_id):
        """
        Method for obtaining a user's followers

        Parameters:
        user_id (int) -- User's ID

        Return:
        list[User]
        """

        return self.__client.get_followers(user_id)

    def get_following(self,user_id):
        """
        Method to obtain the followings of a user

        Parameters:
        user_id (int) -- User's ID

        Return:
        list[User]
        """

        return self.__client.get_following(user_id)

    def get_game_by_id(self,game_id):
        """
        Method for obtaining a category from its ID

        Parameters:
        game_id -- Category's ID

        Return:
        Game -- If the category exists
        None -- If the category doesn't exists
        """

        return self.__client.get_game_by_id(game_id)

    def get_game_by_name(self,game_name):
        """
        Method for obtaining a category from its name

        Parameters:
        game_name -- Category's name

        Return:
        Game -- If the category exists
        None -- If the category doesn't exists
        """

        return self.__client.get_game_by_name(game_name)

    def get_stream_by_channel_id(self,id):
        """
        Method for obtaining a stream from its channel's ID

        Parameters:
        id -- Channel's ID

        Return:
        Stream -- If the channel is live
        None -- If the channel is not live
        """

        return self.__client.get_stream_by_channel_id(id)

    def get_stream_by_username(self,username):
        """
        Method for obtaining a stream from its channel's name

        Parameters:
        username -- Channel's name

        Return:
        Stream -- If the stream is live
        None -- If the stream is not live
        """

        return self.__client.get_stream_by_username(username)

    def get_top_games(self,count=20):
        """
        Get the most viewed categories in Twitch

        Parameters:
        count (int) -- Number of categories to return

        Return:
        list[Game]
        """

        return self.__client.get_top_games(count)

    def get_user_by_id(self,id):
        """
        Method for obtaining a user from his ID

        Parameters: 
        id (int) -- User's ID

        Return:
        User -- If the user exists
        None -- If the user doesn't exist
        """

        return self.__client.get_user_by_id(id)

    def get_user_by_name(self,username):
        """
        Method for obtaining a user from his name

        Parameters: 
        username (str) -- User's name

        Return:
        User -- If the user exists
        None -- If the user doesn't exist
        """

        return self.__client.get_user_by_name(username)

    def get_cheermotes(self,channel_id=None):
        """
        Method for obtaining emotes

        Parameters:
        channel_id (int) -- ID of a channel

        Return:
        dict
        """

        return self.__client.get_cheermotes(channel_id)

    def get_clips_by_channel_id(self,channel_id):
        """
        Method for obtaining clips from a channel

        Parameters:
        channel_id (int) -- Channel's ID

        Return:
        list[dict]
        """

        return self.__client.get_user_by_name(channel_id)

    def get_clips_by_game_id(self,game_id):
        """
        Method for obtaining clips from a category

        Parameters:
        game_id (int) -- Category's ID

        Return:
        list[dict]
        """

        return self.__client.get_clips_by_game_id(game_id)

    def get_clips_by_clip_id(self,clip_id):
        """
        Method for obtaining a clip from its ID

        Parameters:
        clip_id (int) -- Clip's ID

        Return:
        dict -- If the clip exists
        None -- If the clip doesn't exist
        """

        return self.__client.get_clips_by_clip_id(clip_id)

    def get_hype_train_events(self,channel_id):
        """
        Method for obtaining hype train events

        Parameters:
        channel_id (int) -- Channel's ID

        Return:
        list[str] -- If the channel exists
        None -- If the channel doesn't exist
        """

        return self.__client.get_hype_train_events(channel_id)

    def get_streams_by_game_id(self,game_id,count=20):
        """
        Method for obtaining streams from the ID of a category

        Parameters:
        game_id (int) -- Category's ID
        count (int) -- Number of streams to obtain

        Return:
        list[dict] -- If the category exists
        None -- If the category doesn't exist
        """

        return self.__client.get_streams_by_game_id(game_id,count)

    def get_streams_by_language(self,language,count=20):
        """
        Method for obtaining streams in a language

        Parameters:
        language (str) -- Streams' language
        count (int) -- Number of streams to obtain

        Return:
        list[dict] -- If the language exists
        None -- If the language doesn't exist
        """

        return self.__client.get_streams_by_language(language,count)

    def get_stream_tags(self,channel_id=None,tag_id=None,count=20):
        """
        Method for obtaining the tags of a stream

        Parameters:
        channel_id (int) -- Channel's ID
        tag_id (int) -- ID of a tag
        count (int) -- Number of streams to obtain

        Return:
        list[dict] -- If the channel and the tag exist
        None -- If the channel or the tag doesn't exist
        """

        return self.__client.get_stream_tags(channel_id,tag_id,count)

    def get_videos_by_id(self,id):
        """
        Method for obtaining a video from its ID

        Parameters:
        id (int) -- Video's ID

        Return:
        dict -- If the video exists
        None -- If the video doesn't exist
        """

        return self.__client.get_videos_by_id(id)

    def get_videos_by_user_id(self,user_id):
        """
        Method for obtaining the videos of a channel

        Parameters:
        user_id (int) -- Channel's ID

        Return:
        list[dict] -- If the channel exists
        None -- If the channel doesn't exist
        """

        return self.__client.get_videos_by_user_id(user_id)

    def get_videos_by_game_id(self,game_id):
        """
        Method for obtaining the videos of a category

        Parameters:
        game_id (int) -- Category's ID

        Return:
        list[dict] -- If the category exists
        None -- If the category doesn't exist
        """

        return self.__client.get_videos_by_game_id(game_id)

    def ban(self,channel,user,reason=""):
        """
        Method for banning a user from a channel

        Parameters:
        channel (str) -- Channel who bans
        user (str) -- User to ban
        reason (str) -- Reason of the ban
        """

        self.__send_privmsg(channel,f"/ban @{user} {reason}")

    def block(self,channel,user):
        """
        Method for blocking a user

        Parameters:
        channel (str) -- Channel who blocks
        user (str) -- User to block
        """

        self.__send_privmsg(channel,f"/block @{user}")

    def clear(self,channel):
        """
        Method for clearing the chat

        Parameters:
        channel (str) -- Channel to clean the chat
        """

        self.__send_privmsg(channel,"/clear")

    def color(self,channel,color):
        """
        Method to change the color of the channel's name in the chat

        Parameters:
        channel (str) -- Channel to change color
        color (str) -- New color's name
        """

        self.__send_privmsg(channel,f"/color {color}")

    def commercial(self,channel,duration=30):
        """
        Method for placing advertising in the channel

        Parameters:
        channel (str) -- Channel on which start the commercial
        duration (int) -- Duration of advertising
        """

        self.__send_privmsg(channel,f"/commercial {duration}")

    def emoteonly(self,channel):
        """
        Method for activating the "emotes only" mode

        Parameters:
        channel (str) -- Channel on which activate the mode
        """

        self.__send_privmsg(channel,"/emoteonly")

    def emoteonly_off(self,channel):
        """
        Method for disabling "emotes only" mode

        Parameters:
        channel (str) -- Channel on which disable the mode
        """

        self.__send_privmsg(self.name,"/emoteonlyoff")

    def followers(self,channel):
        """
        Method for activating the "followers only" mode

        Parameters:
        channel (str) -- Channel on which activate the mode
        """

        self.__send_privmsg(channel,"/followers")

    def followers_off(self,channel):
        """
        Method for disabling the "followers only" mode

        Parameters:
        channel (str) -- Channel on which disable the mode
        """

        self.__send_privmsg(channel,"/followersoff")

    def host(self,channel,username):
        """
        Method for hosting another channel

        Parameters:
        channel (str) -- Name of the channel who hosts
        username (str) -- Name of the channel to host
        """

        self.__send_privmsg(channel,f"/host {username}")

    def marker(self,channel,description=""):
        """
        Method for leaving a mark on the channel's stream

        Parameters:
        channel (str) -- Channel in which leave the mark
        description (str) -- Mark's description
        """

        self.__send_privmsg(channel,f"/marker {description}")

    def mod(self,channel,username):
        """
        Method for making a user mod

        Parameters:
        channel (str) -- Channel who promotes the user
        username (str) -- Name of the user to be promoted
        """

        self.__send_privmsg(channel,f"/mod {username}")

    def raid(self,channel,username):
        """
        Method for raiding another channel

        Parameters:
        channel (str) -- Name of the channel who raids
        username (str) -- Name of the channel to raid
        """

        self.__send_privmsg(channel,f"/raid {username}")

    def send(self,channel,text):
        """
        Method for sending a message by chat

        Parameters:
        channel (str) -- Owner of the chat
        text (str) -- Message's text
        """

        self.__send_privmsg(channel,text)

    def send_me(self,channel,text):
        """
        Method for sending a message by chat

        Parameters:
        channel (str) -- Owner of the chat
        text (str) -- Message's text
        """

        self.__send_privmsg(channel,f"/me {text}")

    def slow(self,channel,duration):
        """
        Method for activating the "slow" mode

        Parameters:
        channel (str) -- Channel on which activate the mode
        duration (int) -- Time between messages
        """

        self.__send_privmsg(channel,f"/slow {duration}")

    def slow_off(self,channel):
        """
        Method for disabling the "slow" mode

        Parameters:
        channel (str) -- Channel on which disable the mode
        """

        self.__send_privmsg(channel,f"/slow_off")

    def subscribers(self,channel):
        """
        Method for activating the "subscribers only" mode

        Parameters:
        channel (str) -- Channel on which activate the mode
        """

        self.__send_privmsg(channel,"/subscribers")

    def subscribers_off(self,channel):
        """
        Method for disabling "subscriber only" mode

        Parameters:
        channel (str) -- Channel on which disable the mode
        """

        self.__send_privmsg(channel,"/subscribersoff")

    def timeout(self,channel,user,duration=600,reason=""):
        """
        Method for temporarily expelling a user

        Parameters:
        channel (str) -- Channel who ejects
        user (str) -- Name of the user to expel
        duration (int) -- Ejecting time
        reason (str) -- Reason for expulsion
        """

        self.__send_privmsg(channel,f"/timeout @{user} {duration} {reason}")

    def unban(self,channel,user):
        """
        Method for undoing the ban of a user

        Parameters:
        channel (str) -- Name of the channel who readmits
        user (str) -- Name of the user to readmit
        """

        self.__send_privmsg(channel,f"/unban @{user}")

    def unblock(self,channel,user):
        """
        Method for unblocking a user

        Parameters:
        channel (str) -- Name of the channel who unblocks
        user (str) -- Name of the user to unblock
        """

        self.__send_privmsg(channel,f"/unblock @{user}")

    def uniquechat(self,channel):
        """
        Method for activating the "unique" mode

        Parameters:
        channel (str) -- Channel on which activate the mode
        """

        self.__send_privmsg(channel,"/uniquechat")

    def uniquechat_off(self,channel):
        """
        Method for disabling the "unique" mode

        Parameters:
        channel (str) -- Channel on which disable the mode
        """

        self.__send_privmsg(channel,"/uniquechatoff")

    def unhost(self,channel):
        """
        Method for unhosting the hosted channel

        Parameters:
        channel (str) -- Channel who unhosts
        """

        self.__send_privmsg(channel,f"/unhost")

    def unmod(self,channel,username):
        """
        Method to remove the moderator's rank from a user

        Parameters:
        channel (str) -- Channel who removes the moderator's rank
        username (str) -- User's name
        """

        self.__send_privmsg(channel,f"/unmod {username}")

    def unraid(self,channel):
        """
        Method to cancel an raid

        Parameters:
        channel (str) -- Channel who unraids
        """

        self.__send_privmsg(channel,f"/unraid")

    def unvip(self,channel,username):
        """
        Method to remove the vip range from a user

        Parameters:
        channel (str) -- Channel who remove's the vip range
        username (str) -- User's name
        """

        self.__send_privmsg(channel,f"/unvip {username}")

    def vip(self,channel,username):
        """
        Method for making a user vip

        Parameters:
        channel (str) -- Channel who makes a user vip
        username (str) -- User's name
        """

        self.__send_privmsg(channel,f"/vip {username}")

    def whisper(self,channel,user,text):
        """
        Method for whispering to a user

        Parameters:
        channel (str) -- Channel on which send the whisp
        user (str) -- User's name
        text (str) -- Whisper's text
        """

        self.__send_privmsg(channel,f"/w {user} {text}")

    def add_method_after_commands(self,name,method):
        """
        Method to add to the bot methods that will be executed after each command

        Parameters:
        name (str) -- Method's name
        method (func) -- Method to be executed after each command
        """

        self.custom_methods_after_commands[name]=method

    def add_method_before_commands(self,name,method):
        """
        Method to add to the bot methods that will be executed before each command

        Parameters:
        name (str) -- Method's name
        method (func) -- Method to be executed before each command
        """

        self.custom_methods_before_commands[name]=method

    def remove_check(self,name):
        """
        Method for removing a check from the bot

        Parameters:
        name (str) -- Check's name
        """

        self.custom_checks.pop(name,None)

    def remove_listener(self,name):
        """
        Method for removing a listener from the bot

        Parameters:
        name (str) -- Listener's name
        """

        self.custom_listeners.pop(name,None)

    def remove_method_after_commands(self,name):
        """
        Method to remove a method that is executed after each command

        Parameters:
        name (str) -- Method's name
        """

        self.custom_methods_after_commands.pop(name,None)

    def remove_method_before_commands(self,name):
        """
        Method to remove a method that is executed before each command

        Parameters:
        name (str) -- Method's name
        """

        self.custom_methods_before_commands.pop(name,None)