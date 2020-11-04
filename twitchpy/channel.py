import ssl
import socket
import requests

class Channel():
    """
    Class that represents a channel
    """

    def __init__(self,oauth_token,client_id,client_secret,name,game_name,broadcaster_language,title):
        """
        Parameters:
        oauth_token (str) -- OAuth token to identify the application
        client_id (str) -- Client ID to identify the application
        client_secret (str) -- Client secret to identify the application
        name (str) -- Channel's name
        game_name (str) -- Channel's category's name
        broadcaster_language (str) -- Channel's language
        title -- Title in the channel
        """

        self.__oauth_token=oauth_token
        self.__client_id=client_id
        self.__client_secret=client_secret
        self.__access_token=self.__get_access_token()
        self.__irc_server="irc.chat.twitch.tv"
        self.__irc_port=6697
        self.name=name
        self.game_name=game_name
        self.broadcaster_language=broadcaster_language
        self.title=title
        self.__connect()

    def __get_access_token(self):
        url="https://id.twitch.tv/oauth2/token"
        payload={"client_id":self.__client_id,"client_secret":self.__client_secret,"grant_type":"client_credentials"}

        response=requests.post(url,json=payload).json()

        return response["access_token"]

    def __connect(self):
        self.irc=ssl.wrap_socket(socket.socket())
        self.irc.connect((self.__irc_server,self.__irc_port))
        
        self.__send_command(f"PASS {self.__oauth_token}")
        self.__send_command(f"NICK {self.name}")

        self.__send_command(f"JOIN #{self.name}")

    def __send_command(self,command):
        self.irc.send((command+"\r\n").encode())

    def __send_privmsg(self,channel,text):
        self.__send_command(f"PRIVMSG #{channel} :{text}")

    def ban(self,user,reason=""):
        """
        Method for banning a user

        Parameters:
        user (str) -- User to ban
        reason (str) -- Reason of the ban
        """

        self.__send_privmsg(self.name,f"/ban @{user} {reason}")

    def block(self,user):
        """
        Method for blocking a user

        Parameters:
        user (str) -- User to block
        """

        self.__send_privmsg(self.name,f"/block @{user}")

    def clear(self):
        """
        Method for clearing the chat
        """

        self.__send_privmsg(self.name,"/clear")

    def color(self,color):
        """
        Method to change the color of the channel's name in the chat

        Parameters:
        color (str) -- New color's name
        """

        self.__send_privmsg(self.name,f"/color {color}")

    def commercial(self,duration=30):
        """
        Method for placing advertising in the channel

        Parameters:
        duration (int) -- Duration of advertising
        """

        self.__send_privmsg(self.name,f"/commercial {duration}")

    def emoteonly(self):
        """
        Method for activating the "emotes only" mode
        """

        self.__send_privmsg(self.name,"/emoteonly")

    def emoteonly_off(self):
        """
        Method for disabling "emotes only" mode
        """

        self.__send_privmsg(self.name,"/emoteonlyoff")

    def followers(self):
        """
        Method for activating the "followers only" mode
        """

        self.__send_privmsg(self.name,"/followers")

    def followers_off(self):
        """
        Method for disabling the "followers only" mode
        """

        self.__send_privmsg(self.name,"/followersoff")

    def get_stream(self):
        """
        Method for obtaining information about the channel's stream

        Return:
        Stream -- If the stream is live
        None -- If the stream isn't live
        """

        url=f"https://api.twitch.tv/helix/streams"
        headers={"Authorization": f"Bearer {self.__access_token}","Client-Id":self.__client_id}
        params={"user_login":self.name}

        response=requests.get(url,headers=headers,params=params).json()
        
        try:
            if len(response["data"])>0:
                stream=response["data"][0]
                stream=(stream["id"],stream["user_id"],stream["user_name"],stream["game_id"],stream["type"],stream["title"],stream["viewer_count"],stream["started_at"],stream["language"],stream["thumbnail_url"],stream["tag_ids"],)

                return stream

            else:
                return None
        
        except KeyError:
            return None

    def host(self,username):
        """
        Method for hosting another channel

        Parameters:
        username (str) -- Name of the channel to host
        """

        self.__send_privmsg(self.name,f"/host {username}")

    def marker(self,description=""):
        """
        Method for leaving a mark on the channel's stream

        Parameters:
        description (str) -- Mark's description
        """

        self.__send_privmsg(self.name,f"/marker {description}")

    def mod(self,username):
        """
        Method for making a user mod

        Parameters:
        username (str) -- Name of the user to be promoted
        """

        self.__send_privmsg(self.name,f"/mod {username}")

    def raid(self,username):
        """
        Method for raiding another channel

        Parameters:
        username -- Name of the channel to raid
        """

        self.__send_privmsg(self.name,f"/raid {username}")

    def send(self,text):
        """
        Method for sending a message by chat

        Parameters:
        text (str) -- Message's text
        """

        self.__send_privmsg(self.name,text)

    def send_me(self,text):
        """
        Method to send a message by chat with the color of the channel's name

        Parameters:
        text (str) -- Message' text
        """

        self.__send_privmsg(self.name,f"/me {text}")

    def slow(self,duration):
        """
        Method for activating the "slow" mode

        Parameters:
        duration (int) -- Time between messages
        """

        self.__send_privmsg(self.name,f"/slow {duration}")

    def slow_off(self):
        """
        Method for disabling the "slow" mode
        """

        self.__send_privmsg(self.name,f"/slow_off")

    def subscribers(self):
        """
        Method for activating the "subscribers only" mode
        """

        self.__send_privmsg(self.name,"/subscribers")

    def subscribers_off(self):
        """
        Method for disabling "subscriber only" mode
        """

        self.__send_privmsg(self.name,"/subscribersoff")

    def timeout(self,user,duration=600,reason=""):
        """
        Method for temporarily expelling a user

        Parameters:
        user (str) -- Name of the user to expel
        duration (int) -- Ejecting time
        reason (str) -- Reason for expulsion
        """

        self.__send_privmsg(self.name,f"/timeout @{user} {duration} {reason}")

    def unban(self,user):
        """
        Method for undoing the ban of a user

        Parameters:
        user (str) -- Name of the user to readmit
        """

        self.__send_privmsg(self.name,f"/unban @{user}")

    def unblock(self,user):
        """
        Method for unblocking a user

        Parameters:
        user (str) -- Name of the user to unblock
        """

        self.__send_privmsg(self.name,f"/unblock @{user}")

    def uniquechat(self):
        """
        Method for activating the "unique" mode
        """

        self.__send_privmsg(self.name,"/uniquechat")

    def uniquechat_off(self):
        """
        Method for disabling the "unique" mode
        """

        self.__send_privmsg(self.name,"/uniquechatoff")

    def unhost(self):
        """
        Method for unhosting the hosted channel
        """

        self.__send_privmsg(self.name,f"/unhost")

    def unmod(self,username):
        """
        Method to remove the moderator's rank from a user

        Parameters:
        username (str) -- User's name
        """

        self.__send_privmsg(self.name,f"/unmod {username}")

    def unraid(self):
        """
        Method to cancel an raid
        """

        self.__send_privmsg(self.name,f"/unraid")

    def unvip(self,username):
        """
        Method to remove the vip range from a user

        Parameters:
        username (str) -- User's name
        """

        self.__send_privmsg(self.name,f"/unvip {username}")

    def vip(self,username):
        """
        Method for making a user vip

        Parameters:
        username (str) -- User's name
        """

        self.__send_privmsg(self.name,f"/vip {username}")

    def whisper(self,user,text):
        """
        Method for whispering to a user

        Parameters:
        user (str) -- User's name
        text (str) -- Whisper's text
        """

        self.__send_privmsg(self.name,f"/w {user} {text}")