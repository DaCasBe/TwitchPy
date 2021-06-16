import ssl
import socket
import requests

class Channel():
    """
    Represents a channel
    """

    def __init__(self,oauth_token,client_id,client_secret,name,game_name,broadcaster_language,title):
        """
        Args:
            oauth_token (str): OAuth token to identify the application
            client_id (str): Client ID to identify the application
            client_secret (str): Client secret to identify the application
            name (str): Channel's name
            game_name (str): Channel's category's name
            broadcaster_language (str): Channel's language
            title (str): Title in the channel
        """

        self.__oauth_token=oauth_token
        self.__client_id=client_id
        self.__client_secret=client_secret
        self.__access_token=self.__get_access_token()
        self.__irc_server="irc.chat.twitch.tv"
        self.__irc_port=6697
        self.name=name.replace("@","").lower()
        self.game_name=game_name
        self.broadcaster_language=broadcaster_language
        self.title=title

    def __get_access_token(self):
        url="https://id.twitch.tv/oauth2/token"
        payload={"client_id":self.__client_id,"client_secret":self.__client_secret,"grant_type":"client_credentials"}

        response=requests.post(url,json=payload).json()

        return response["access_token"]

    def connect(self):
        """
        Creates a connection with the channel
        """

        self.irc=ssl.wrap_socket(socket.socket())
        self.irc.connect((self.__irc_server,self.__irc_port))
        
        self.__send_command(f"PASS {self.__oauth_token}")
        self.__send_command(f"NICK {self.name}")

        self.__send_command(f"JOIN #{self.name}")

    def __send_command(self,command):
        self.irc.send((command+"\r\n").encode())

    def __send_privmsg(self,channel,text):
        self.__send_command(f"PRIVMSG #{channel} :{text}")

    def ban(self,username,reason=""):
        """
        Bans a user

        Args:
            username (str): User to ban
            reason (str, optional): Reason of the ban
        """

        username=username.replace("@","").lower()
        self.__send_privmsg(self.name,f"/ban @{username} {reason}")

    def block(self,username):
        """
        Blocks a user

        Args:
            username (str): User to block
        """

        username=username.replace("@","").lower()
        self.__send_privmsg(self.name,f"/block @{username}")

    def clear(self):
        """
        Clears the chat
        """

        self.__send_privmsg(self.name,"/clear")

    def color(self,color):
        """
        Changes the color of the channel's name in the chat

        Args:
            color (str): New color's name
        """

        self.__send_privmsg(self.name,f"/color {color}")

    def commercial(self,duration=30):
        """
        Places advertising in the channel

        Args:
            duration (int, optional): Duration of advertising
        """

        self.__send_privmsg(self.name,f"/commercial {duration}")

    def emoteonly(self):
        """
        Activates the "emotes only" mode
        """

        self.__send_privmsg(self.name,"/emoteonly")

    def emoteonly_off(self):
        """
        Disables "emotes only" mode
        """

        self.__send_privmsg(self.name,"/emoteonlyoff")

    def followers(self):
        """
        Activates the "followers only" mode
        """

        self.__send_privmsg(self.name,"/followers")

    def followers_off(self):
        """
        Disables the "followers only" mode
        """

        self.__send_privmsg(self.name,"/followersoff")

    def host(self,channel):
        """
        Hosts a channel

        Args:
            channel (str): Name of the channel to host
        """

        channel=channel.replace("@","").lower()
        self.__send_privmsg(self.name,f"/host {channel}")

    def marker(self,description=""):
        """
        Leaves a mark on the channel's stream

        Args:
            description (str, optional): Mark's description
        """

        self.__send_privmsg(self.name,f"/marker {description}")

    def mod(self,username):
        """
        Makes a user mod

        Args:
            username (str): Name of the user to be promoted
        """

        username=username.replace("@","").lower()
        self.__send_privmsg(self.name,f"/mod {username}")

    def raid(self,channel):
        """
        Raids another channel

        Args:
            channel (str): Name of the channel to raid
        """

        channel=channel.replace("@","").lower()
        self.__send_privmsg(self.name,f"/raid {channel}")

    def send(self,text):
        """
        Sends a message by chat

        Args:
            text (str): Message's text
        """

        self.__send_privmsg(self.name,text)

    def send_me(self,text):
        """
        Sends a message by chat with the color of the channel's name

        Args:
            text (str): Message' text
        """

        self.__send_privmsg(self.name,f"/me {text}")

    def slow(self,duration):
        """
        Activates the "slow" mode

        Args:
            duration (int): Time between messages
        """

        self.__send_privmsg(self.name,f"/slow {duration}")

    def slow_off(self):
        """
        Disables the "slow" mode
        """

        self.__send_privmsg(self.name,f"/slow_off")

    def subscribers(self):
        """
        Activates the "subscribers only" mode
        """

        self.__send_privmsg(self.name,"/subscribers")

    def subscribers_off(self):
        """
        Disables "subscriber only" mode
        """

        self.__send_privmsg(self.name,"/subscribersoff")

    def timeout(self,username,duration=600,reason=""):
        """
        Expels a user temporarily

        Args:
            username (str): Name of the user to expel
            duration (int, optional): Ejecting time
            reason (str, optional): Reason for expulsion
        """

        username=username.replace("@","").lower()
        self.__send_privmsg(self.name,f"/timeout @{username} {duration} {reason}")

    def unban(self,username):
        """
        Undoes the ban of a user

        Args:
            username (str): Name of the user to readmit
        """

        username=username.replace("@","").lower()
        self.__send_privmsg(self.name,f"/unban @{username}")

    def unblock(self,username):
        """
        Unblocks a user

        Args:
            username (str): Name of the user to unblock
        """

        username=username.replace("@","").lower()
        self.__send_privmsg(self.name,f"/unblock @{username}")

    def uniquechat(self):
        """
        Activates the "unique" mode
        """

        self.__send_privmsg(self.name,"/uniquechat")

    def uniquechat_off(self):
        """
        Disables the "unique" mode
        """

        self.__send_privmsg(self.name,"/uniquechatoff")

    def unhost(self):
        """
        Unhosts the hosted channel
        """

        self.__send_privmsg(self.name,f"/unhost")

    def unmod(self,username):
        """
        Removes the moderator's rank from a user

        Args:
            username (str): User's name
        """

        username=username.replace("@","").lower()
        self.__send_privmsg(self.name,f"/unmod {username}")

    def unraid(self):
        """
        Cancels a raid
        """

        self.__send_privmsg(self.name,f"/unraid")

    def unvip(self,username):
        """
        Removes the vip range from a user

        Args:
            username (str): User's name
        """

        username=username.replace("@","").lower()
        self.__send_privmsg(self.name,f"/unvip {username}")

    def vip(self,username):
        """
        Makes a user vip

        Args:
            username (str): User's name
        """

        username=username.replace("@","").lower()
        self.__send_privmsg(self.name,f"/vip {username}")

    def whisper(self,username,text):
        """
        Whispers to a user

        Args:
            username (str): User's name
            text (str): Whisper's text
        """

        username=username.replace("@","").lower()
        self.__send_privmsg(self.name,f"/w {username} {text}")