import requests
from twitchpy.user import User
from twitchpy.game import Game
from twitchpy.stream import Stream
from twitchpy.channel import Channel

class Client:
    """
    Class that represents a client connection to the Twitch API
    """

    def __init__(self,oauth_token,client_id,client_secret):
        """
        Parámetros:
        oauth_token (str) -- OAuth token to identify the application
        client_id (str) -- Client ID to identify the application
        client_secret (str) -- Client secret to identify the application
        """

        self.oauth_token=oauth_token
        self.client_id=client_id
        self.client_secret=client_secret
        self.__access_token=self.get_access_token()

    def get_access_token(self):
        """
        Method for obtaining a Twitch API access token

        Return:
        str
        """

        url="https://id.twitch.tv/oauth2/token"
        payload={"client_id":self.client_id,"client_secret":self.client_secret,"grant_type":"client_credentials"}

        response=requests.post(url,json=payload).json()

        return response["access_token"]

    def get_chatters(self,channel_name):
        """
        Method for getting users into a channel's chat

        Parameters:
        channel_name (str) -- Channel's name

        Return:
        dict
        """

        url=f"https://tmi.twitch.tv/group/user/{channel_name}/chatters"
        headers={"Authorization": f"Bearer {self.__access_token}","Client-Id":self.client_id}

        response=requests.post(url,headers=headers).json()

        return response["chatters"]

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

        url=f"https://api.twitch.tv/helix/users/follows"
        headers={"Authorization": f"Bearer {self.__access_token}","Client-Id":self.client_id}
        params={"from_id":from_id,"to_id":to_id}

        response=requests.get(url,headers=headers,params=params).json()
        
        if len(response["data"])>0:
            return response["data"][0]["followed_at"]

        else:
            return None

    def get_followers(self,user_id):
        """
        Method for obtaining a user's followers

        Parameters:
        user_id (int) -- User's ID

        Return:
        list[User]
        """

        url=f"https://api.twitch.tv/helix/users/follows"
        headers={"Authorization": f"Bearer {self.__access_token}","Client-Id":self.client_id}
        params={"to_id":user_id}

        response=requests.get(url,headers=headers,params=params).json()

        followers=[]

        for follower in response["data"]:
            user=self.get_user_by_id(follower["from_id"])
            followers.append({"follower":user,"followed_at":follower["followed_at"]})

        return followers

    def get_following(self,user_id):
        """
        Method to obtain the followings of a user

        Parameters:
        user_id (int) -- User's ID

        Return:
        list[User]
        """

        url=f"https://api.twitch.tv/helix/users/follows"
        headers={"Authorization": f"Bearer {self.__access_token}","Client-Id":self.client_id}
        params={"from_id":user_id}

        response=requests.get(url,headers=headers,params=params).json()
        
        followings=[]

        for following in response["data"]:
            user=self.get_user_by_id(following["to_id"])
            followings.append({"follower":user,"followed_at":following["followed_at"]})

        return followings

    def get_game_by_id(self,game_id):
        """
        Method for obtaining a category from its ID

        Parameters:
        game_id -- Category's ID

        Return:
        Game -- If the category exists
        None -- If the category doesn't exists
        """

        url=f"https://api.twitch.tv/helix/games"
        headers={"Authorization": f"Bearer {self.__access_token}","Client-Id":self.client_id}
        params={"id":game_id}

        response=requests.get(url,headers=headers,params=params).json()
        
        if len(response["data"])>0:
            game=Game(response["data"][0]["id"],response["data"][0]["name"],response["data"][0]["box_art_url"])

            return game

        else:
            return None

    def get_game_by_name(self,game_name):
        """
        Method for obtaining a category from its name

        Parameters:
        game_name -- Category's name

        Return:
        Game -- If the category exists
        None -- If the category doesn't exists
        """

        url=f"https://api.twitch.tv/helix/games"
        headers={"Authorization": f"Bearer {self.__access_token}","Client-Id":self.client_id}
        params={"name":game_name}

        response=requests.get(url,headers=headers,params=params).json()
        
        if len(response["data"])>0:
            game=Game(response["data"][0]["id"],response["data"][0]["name"],response["data"][0]["box_art_url"])

            return game

        else:
            return None

    def get_stream_by_channel_id(self,id):
        """
        Method for obtaining a stream from its channel's ID

        Parameters:
        id -- Channel's ID

        Return:
        Stream -- If the channel is live
        None -- If the channel is not live
        """

        url=f"https://api.twitch.tv/helix/streams"
        headers={"Authorization": f"Bearer {self.__access_token}","Client-Id":self.client_id}
        params={"user_id":id}

        response=requests.get(url,headers=headers,params=params).json()
        
        if len(response["data"])>0:
            stream=Stream(response["data"][0]["id"],response["data"][0]["user_id"],response["data"][0]["user_name"],response["data"][0]["game_id"],response["data"][0]["type"],response["data"][0]["title"],response["data"][0]["viewer_count"],response["data"][0]["started_at"],response["data"][0]["language"],response["data"][0]["thumbnail_url"],response["data"][0]["tag_ids"])

            return stream

        else:
            return None

    def get_stream_by_username(self,username):
        """
        Method for obtaining a stream from its channel's name

        Parameters:
        username -- Channel's name

        Return:
        Stream -- If the stream is live
        None -- If the stream is not live
        """

        url=f"https://api.twitch.tv/helix/streams"
        headers={"Authorization": f"Bearer {self.__access_token}","Client-Id":self.client_id}
        params={"user_login":username}

        response=requests.get(url,headers=headers,params=params).json()
        
        if len(response["data"])>0:
            stream=Stream(response["data"][0]["id"],response["data"][0]["user_id"],response["data"][0]["user_name"],response["data"][0]["game_id"],response["data"][0]["type"],response["data"][0]["title"],response["data"][0]["viewer_count"],response["data"][0]["started_at"],response["data"][0]["language"],response["data"][0]["thumbnail_url"],response["data"][0]["tag_ids"])

            return stream

        else:
            return None

    def get_top_games(self,count=20):
        """
        Get the most viewed categories in Twitch

        Parameters:
        count (int) -- Number of categories to return

        Return:
        list[Game]
        """

        url=f"https://api.twitch.tv/helix/games/top"
        headers={"Authorization": f"Bearer {self.__access_token}","Client-Id":self.client_id}
        params={"first":count}

        response=requests.get(url,headers=headers,params=params).json()
        games=[]
        
        for game in response["data"]:
            games.append(self.get_game_by_id(game["id"])[0])

        return games

    def get_user_by_id(self,id):
        """
        Method for obtaining a user from his ID

        Parameters: 
        id (int) -- User's ID

        Return:
        User -- If the user exists
        None -- If the user doesn't exist
        """

        url=f"https://api.twitch.tv/helix/users"
        headers={"Authorization": f"Bearer {self.__access_token}","Client-Id":self.client_id}
        params={"id":id}

        response=requests.get(url,headers=headers,params=params).json()
        
        if len(response["data"])>0:
            user=response["data"][0]
            user=User(user["id"],user["login"],user["display_name"],user["type"],user["broadcaster_type"],user["description"],user["profile_image_url"],user["offline_image_url"],user["view_count"])
            
            return user

        else:
            return None

    def get_user_by_name(self,username):
        """
        Method for obtaining a user from his name

        Parameters: 
        username (str) -- User's name

        Return:
        User -- If the user exists
        None -- If the user doesn't exist
        """

        url=f"https://api.twitch.tv/helix/users"
        headers={"Authorization": f"Bearer {self.__access_token}","Client-Id":self.client_id}
        params={"login":username}

        response=requests.get(url,headers=headers,params=params).json()
        
        if len(response["data"])>0:
            user=response["data"][0]
            user=User(user["id"],user["login"],user["display_name"],user["type"],user["broadcaster_type"],user["description"],user["profile_image_url"],user["offline_image_url"],user["view_count"])
            
            return user

        else:
            return None

    def get_channel(self,user_id):
        """
        Method that returns a channel

        Parameters:
        id (int) -- Channel's ID

        Return:
        Channel -- If the channel exists
        None -- If the channel doesn't exist
        """

        url=f"https://api.twitch.tv/helix/channels"
        headers={"Authorization": f"Bearer {self.__access_token}","Client-Id":self.client_id}
        params={"broadcaster_id":user_id}

        response=requests.get(url,headers=headers,params=params).json()
        
        if len(response["data"])>0:
            channel=response["data"][0]
            channel=Channel(self.oauth_token,self.client_id,self.client_secret,self.get_user_by_id(channel["broadcaster_id"]).login,channel["game_name"],channel["broadcaster_language"],channel["title"])
            
            return channel

        else:
            return None

    def get_cheermotes(self,channel_id=None):
        """
        Method for obtaining emotes

        Parameters:
        channel_id (int) -- ID of a channel

        Return:
        dict
        """

        url="https://api.twitch.tv/helix/bits/cheermotes"
        headers={"Authorization": f"Bearer {self.__access_token}","Client-Id":self.client_id}

        if channel_id==None:
            response=requests.get(url,headers=headers).json()

        else:
            params={"broadcaster_id":channel_id}
            response=requests.get(url,headers=headers,params=params).json()

        if len(response["data"])>0:
            return response["data"]

        else:
            return None

    def get_clips_by_channel_id(self,channel_id):
        """
        Method for obtaining clips from a channel

        Parameters:
        channel_id (int) -- Channel's ID

        Return:
        list[dict]
        """

        url="https://api.twitch.tv/helix/clips"
        headers={"Authorization": f"Bearer {self.__access_token}","Client-Id":self.client_id}
        params={"broadcaster_id":channel_id}

        response=requests.get(url,headers=headers,params=params).json()

        if len(response["data"])>0:
            return response["data"]

        else:
            return None

    def get_clips_by_game_id(self,game_id):
        """
        Method for obtaining clips from a category

        Parameters:
        game_id (int) -- Category's ID

        Return:
        list[dict]
        """

        url="https://api.twitch.tv/helix/clips"
        headers={"Authorization": f"Bearer {self.__access_token}","Client-Id":self.client_id}
        params={"game_id":game_id}

        response=requests.get(url,headers=headers,params=params).json()

        if len(response["data"])>0:
            return response["data"]

        else:
            return None

    def get_clips_by_clip_id(self,clip_id):
        """
        Method for obtaining a clip from its ID

        Parameters:
        clip_id (int) -- Clip's ID

        Return:
        dict -- If the clip exists
        None -- If the clip doesn't exist
        """

        url="https://api.twitch.tv/helix/clips"
        headers={"Authorization": f"Bearer {self.__access_token}","Client-Id":self.client_id}
        params={"id":clip_id}

        response=requests.get(url,headers=headers,params=params).json()

        if len(response["data"])>0:
            return response["data"][0]

        else:
            return None

    def get_hype_train_events(self,channel_id):
        """
        Method for obtaining hype train events

        Parameters:
        channel_id (int) -- Channel's ID

        Return:
        list[str] -- If the channel exists
        None -- If the channel doesn't exist
        """

        url="https://api.twitch.tv/helix/hypetrain/events"
        headers={"Authorization": f"Bearer {self.__access_token}","Client-Id":self.client_id}
        params={"broadcaster_id":channel_id}

        response=requests.get(url,headers=headers,params=params).json()

        if len(response["data"])>0:
            return response["data"]

        else:
            return None

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

        url="https://api.twitch.tv/helix/streams"
        headers={"Authorization": f"Bearer {self.__access_token}","Client-Id":self.client_id}
        params={"game_id":game_id,"first":f"{count+1}"}

        response=requests.get(url,headers=headers,params=params).json()

        if len(response["data"])>0:
            return response["data"]

        else:
            return None

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

        url="https://api.twitch.tv/helix/streams"
        headers={"Authorization": f"Bearer {self.__access_token}","Client-Id":self.client_id}
        params={"language":language,"first":count}

        response=requests.get(url,headers=headers,params=params).json()

        if len(response["data"])>0:
            return response["data"]

        else:
            return None

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

        url="https://api.twitch.tv/helix/tags/streams"
        headers={"Authorization": f"Bearer {self.__access_token}","Client-Id":self.client_id}

        if channel_id==None:
            if tag_id==None:
                response=requests.get(url,headers=headers).json()

            else:
                params={"tag_id":tag_id,"first":count}
                response=requests.get(url,headers=headers,params=params).json()

        else:
            if tag_id==None:
                response=requests.get(url,headers=headers).json()

            else:
                params={"broadcaster_id":channel_id,"tag_id":tag_id,"first":count}
                response=requests.get(url,headers=headers,params=params).json()

        if len(response["data"])>0:
            return response["data"]

        else:
            return None

    def get_videos_by_id(self,id):
        """
        Method for obtaining a video from its ID

        Parameters:
        id (int) -- Video's ID

        Return:
        dict -- If the video exists
        None -- If the video doesn't exist
        """

        url="https://api.twitch.tv/helix/videos"
        headers={"Authorization": f"Bearer {self.__access_token}","Client-Id":self.client_id}
        params={"id":id}

        response=requests.get(url,headers=headers,params=params).json()

        if len(response["data"])>0:
            return response["data"][0]

        else:
            return None

    def get_videos_by_user_id(self,user_id):
        """
        Method for obtaining the videos of a channel

        Parameters:
        user_id (int) -- Channel's ID

        Return:
        list[dict] -- If the channel exists
        None -- If the channel doesn't exist
        """

        url="https://api.twitch.tv/helix/videos"
        headers={"Authorization": f"Bearer {self.__access_token}","Client-Id":self.client_id}
        params={"user_id":user_id}

        response=requests.get(url,headers=headers,params=params).json()

        if len(response["data"])>0:
            return response["data"]

        else:
            return None

    def get_videos_by_game_id(self,game_id):
        """
        Method for obtaining the videos of a category

        Parameters:
        game_id (int) -- Category's ID

        Return:
        list[dict] -- If the category exists
        None -- If the category doesn't exist
        """

        url="https://api.twitch.tv/helix/videos"
        headers={"Authorization": f"Bearer {self.__access_token}","Client-Id":self.client_id}
        params={"game_id":game_id}

        response=requests.get(url,headers=headers,params=params).json()

        if len(response["data"])>0:
            return response["data"]

        else:
            return None