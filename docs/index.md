# TwitchPy

## Installation

TwitchPy requires Python 3.6 or higher.

~~~
pip install twitchpy
~~~

## Getting started

TwitchPy uses many endpoints which may require different tokens and IDs.

+ IRC endpoints which require an OAuth token. Log in to Twitch with the bot's account and visit: <https://twitchapps.com/tmi/>

+ HTTP endpoints which require a client ID. Register a Twitch application with the bot's account: <https://dev.twitch.tv/>

+ HTTP endpoints which require an OAuth token and certain scopes. *To be documented.*

## Client

~~~
class Client(oauth_token,client_id,client_secret,code="")
~~~

Represents a client connection to the Twitch API

**Args**:

+ oauth_token (str): OAuth Token

+ client_id (str): Client ID

+ client_secret (str): Client secret

+ code (str, optional): Authorization code

### Start commercial

~~~
function start_commercial(broadcaster_id,length)
~~~

Starts a commercial on a specified channel

**Args**:

+ broadcaster_id (int): ID of the channel requesting a commercial

+ length (int): Desired length of the commercial in seconds  
                Valid options are 30, 60, 90, 120, 150 and 180

**Raises**:

+ twitchpy.errors.ClientError

**Returns**: list

### Get extension analytics

~~~
function get_extension_analytics(ended_at="",extension_id="",first=20,started_at="",type="")
~~~

Gets a URL that Extension developers can use to download analytics reports for their Extensions  
The URL is valid for 5 minutes

**Args**:

+ ended_at (str, optional): Ending date/time for returned reports, in RFC3339 format with the hours, minutes, and seconds zeroed out and the UTC timezone: YYYY-MM-DDT00:00:00Z  
                            If this is provided, started_at also must be specified

+ extension_id (str, optional): Client ID value assigned to the extension when it is created

+ first (int, optional): Maximum number of objects to return  
                         Default: 20

+ started_at (str, optional): Starting date/time for returned reports, in RFC3339 format with the hours, minutes, and seconds zeroed out and the UTC timezone: YYYY-MM-DDT00:00:00Z  
                              This must be on or after January 31, 2018  
                              If this is provided, ended_at also must be specified

+ type (str, optional): Type of analytics report that is returned  
                        Valid values: "overview_v2"

**Raises**:

+ twitchpy.errors.ClientError

**Returns**: list

### Get game analytics

~~~
function get_game_analytics(first=20,game_id="",type="")
~~~

Gets a URL that game developers can use to download analytics reports for their games  
The URL is valid for 5 minutes

**Args**:

+ ended_at (str, optional): Ending date/time for returned reports, in RFC3339 format with the hours, minutes, and seconds zeroed out and the UTC timezone: YYYY-MM-DDT00:00:00Z  
                            If this is provided, started_at also must be specified

+ first (int, optional): Maximum number of objects to return  
                         Default: 20

+ game_id (str, optional): Game ID

+ started_at (str, optional): Starting date/time for returned reports, in RFC3339 format with the hours, minutes, and seconds zeroed out and the UTC timezone: YYYY-MM-DDT00:00:00Z  
                              If this is provided, ended_at also must be specified

+ type (str, optional): Type of analytics report that is returned  
                        Valid values: "overview_v2"

**Raises**:

+ twitchpy.errors.ClientError

**Returns**: list

### Get bits leaderboard

~~~
function get_bits_leaderboard(count=10,period="all",started_at="",user_id="")
~~~

Gets a ranked list of Bits leaderboard information for a broadcaster

**Args**:

+ count (int, optional): Number of results to be returned  
                         Maximum: 100  
                         Default: 10

+ period (str, optional): Time period over which data is aggregated (PST time zone)  
                          This parameter interacts with started_at  
                          Default: "all"  
                          Valid values: "day", "week", "month", "year", "all"

+ started_at (str, optional): Timestamp for the period over which the returned data is aggregated  
                              Must be in RFC 3339 format  
                              This value is ignored if period is "all"

+ user_id (str, optional): ID of the user whose results are returned  
                           As long as count is greater than 1, the returned data includes additional users, with Bits amounts above and below the user specified

**Raises**:

+ twitchpy.errors.ClientError

**Returns**: list

### Get cheermotes

~~~
function get_cheermotes(broadcaster_id="")
~~~

Retrieves the list of available Cheermotes  
Cheermotes returned are available throughout Twitch, in all Bits-enabled channels

**Args**:

+ broadcaster_id (str, optional): ID for the broadcaster who might own specialized Cheermotes

**Raises**:

+ twitchpy.errors.ClientError

**Returns**: list

### Get extension transactions

~~~
function get_extension_transactions(extension_id,id="",first=20)
~~~

Allows extension back end servers to fetch a list of transactions that have occurred for their extension across all of Twitch  
A transaction is a record of a user exchanging Bits for an in-Extension digital good

**Args**:

+ extension_id (str): ID of the extension to list transactions for

+ id (list, optional): Transaction IDs to look up  
                       Maximum: 100

+ first (int, optional): Maximum number of objects to return  
                         Default: 20

**Raises**:

+ twitchpy.errors.ClientError

**Returns**: list

### Get channel

~~~
function get_channel(broadcaster_id)
~~~

Gets a channel

**Args**:

+ broadcaster_id (str): ID of the channel to be updated

**Raises**:

+ twitchpy.errors.ClientError

**Returns**: Channel

### Modify channel information

~~~
function modify_channel_information(broadcaster_id,game_id="",broadcaster_language="",title="",delay=0)
~~~

Modifies channel information for users  
game_id, broadcaster_language, title and delay parameters are optional, but at least one parameter must be provided

**Args**:

+ broadcaster_id (str): ID of the channel to be updated

+ game_id (str, optional): The current game ID being played on the channel

+ broadcaster_language (str, optional): The language of the channel  
                                        A language value must be either the ISO 639-1 two-letter code for a supported stream language or “other”

+ title (str, optional): The title of the stream

+ delay (int ,optional): Stream delay in seconds  
                         Stream delay is a Twitch Partner feature

**Raises**:

+ twitchpy.errors.FewArgumentsError

### Get channel editors

~~~
function get_channel_editors(broadcaster_id)
~~~

Gets a list of users who have editor permissions for a specific channel

**Args**:

+ broadcaster_id (str): Broadcaster’s user ID associated with the channel

**Raises**:

+ twitchpy.errors.ClientError

**Returns**: list

### Create custom reward

~~~
function create_custom_reward(broadcaster_id,title,cost,prompt="",is_enabled=True,background_color="",is_user_input_required=False,is_max_per_stream_enabled=False,max_per_stream=None,is_max_per_user_per_stream_enabled=False,max_per_user_per_stream=None,is_global_cooldown_enabled=False,global_cooldown_seconds=None,should_redemptions_skip_request_queue=False)
~~~

Creates a Custom Reward on a channel

**Args**:

+ broadcaster_id (str): ID of the channel creating a reward

+ title (str): The title of the reward

+ cost (int): The cost of the reward

+ prompt (str, optional): The prompt for the viewer when they are redeeming the reward

+ is_enabled (bool, optional): Is the reward currently enabled, if false the reward won’t show up to viewers  
                               Default: true

+ background_color (str, optional): Custom background color for the reward  
                                    Format: Hex with # prefix

+ is_user_input_required (bool, optional): Does the user need to enter information when redeeming the reward  
                                           Default: false

+ is_max_per_stream_enabled (bool, optional): Whether a maximum per stream is enabled  
                                              Default: false

+ max_per_stream (int, optional): The maximum number per stream if enabled  
                                  Required when any value of is_max_per_stream_enabled is included

+ is_max_per_user_per_stream_enabled (bool, optional): Whether a maximum per user per stream is enabled  
                                                       Default: false

+ max_per_user_per_stream (int, optional): The maximum number per user per stream if enabled  
                                           Required when any value of is_max_per_user_per_stream_enabled is included

+ is_global_cooldown_enabled (bool, optional): Whether a cooldown is enabled  
                                               Default: false

+ global_cooldown_seconds (int, optional): The cooldown in seconds if enabled  
                                           Required when any value of is_global_cooldown_enabled is included

+ should_redemptions_skip_request_queue (bool, optional): Should redemptions be set to FULFILLED status immediately when redeemed and skip the request queue instead of the normal UNFULFILLED status  
                                                          Default: false

**Raises**:

+ twitchpy.errors.ClientError

**Returns**: list

### Delete custom reward

~~~
function delete_custom_reward(broadcaster_id,id):
~~~

Deletes a Custom Reward on a channel  
The Custom Reward specified by id must have been created by the client_id attached to the OAuth token in order to be deleted  
Any UNFULFILLED Custom Reward Redemptions of the deleted Custom Reward will be updated to the FULFILLED status

**Args**:

+ broadcaster_id (str): Provided broadcaster_id must match the user_id in the user OAuth token

+ id (str): ID of the Custom Reward to delete  
            Must match a Custom Reward on broadcaster_id’s channel

### Get custom reward

~~~
function get_custom_reward(broadcaster_id,id=[],only_manageable_rewards=False)
~~~

Returns a list of Custom Reward objects for the Custom Rewards on a channel

**Args**:

+ broadcaster_id (str): Provided broadcaster_id must match the user_id in the user OAuth token

+ id (list, optional): This parameter filters the results and only returns reward objects for the Custom Rewards with matching ID  
                       Maximum: 50

+ only_manageable_rewards (bool, optional): When set to true, only returns custom rewards that the calling broadcaster can manage  
                                            Default: false

**Raises**:

+ twitchpy.errors.ClientError

**Returns**: list

### Get custom reward redemption

~~~
function get_custom_reward_redemption(broadcaster_id,reward_id,id="",status="",sort="OLDEST",first=20)
~~~

Returns Custom Reward Redemption objects for a Custom Reward on a channel that was created by the same client_id  
Developers only have access to get and update redemptions for the rewards created programmatically by the same client_id

**Args**:

+ broadcaster_id (str): Provided broadcaster_id must match the user_id in the user OAuth token

+ reward_id (str): When ID is not provided, this parameter returns Custom Reward Redemption objects for redemptions of the Custom Reward with ID reward_id

+ id (list, optional): When id is not provided, this param filters the results and only returns Custom Reward Redemption objects for the redemptions with matching ID  
                       Maximum: 50

+ status (str, optional): This param filters the Custom Reward Redemption objects for redemptions with the matching status  
                          Can be one of UNFULFILLED, FULFILLED or CANCELED

+ sort (str, optional): Sort order of redemptions returned when getting the Custom Reward Redemption objects for a reward  
                        One of: OLDEST, NEWEST  
                        Default: OLDEST

+ first (int, optional): Number of results to be returned when getting the Custom Reward Redemption objects for a reward  
                         Default: 20

**Raises**:

+ twitchpy.errors.ClientError

**Returns**: list

### Update custom reward

~~~
function update_custom_reward(broadcaster_id,id,title="",prompt="",cost=None,background_color="",is_enabled=None,is_user_input_required=None,is_max_per_stream_enabled=None,max_per_stream=None,is_max_per_user_per_stream_enabled=False,max_per_user_per_stream=None,is_global_cooldown_enabled=False,global_cooldown_seconds=None,is_paused=None,should_redemptions_skip_request_queue=None)
~~~

Updates a Custom Reward created on a channel  
The Custom Reward specified by id must have been created by the client_id attached to the user OAuth token

**Args**:

+ broadcaster_id (str): Provided broadcaster_id must match the user_id in the user OAuth token

+ id (str): ID of the Custom Reward to update  
            Must match a Custom Reward on the channel of the broadcaster_id

+ title (str, optional): The title of the reward

+ prompt (str, optional): The prompt for the viewer when they are redeeming the reward

+ cost (int, optional): The cost of the reward

+ background_color (str, optional): Custom background color for the reward as a hexadecimal value

+ is_enabled (bool, optional): Is the reward currently enabled, if false the reward won’t show up to viewers

+ is_user_input_required (bool, optional): Does the user need to enter information when redeeming the reward

+ is_max_per_stream_enabled (bool, optional): Whether a maximum per stream is enabled  
                                              Required when any value of max_per_stream is included

+ max_per_stream (int, optional): The maximum number per stream if enabled  
                                  Required when any value of is_max_per_stream_enabled is included

+ is_max_per_user_per_stream_enabled (bool, optional): Whether a maximum per user per stream is enabled  
                                                       Required when any value of max_per_user_per_stream is included

+ max_per_user_per_stream (int, optional): The maximum number per user per stream if enabled  
                                           Required when any value of is_max_per_user_per_stream_enabled is included

+ is_global_cooldown_enabled (bool, optional): Whether a cooldown is enabled  
                                               Required when any value of global_cooldown_seconds is included

+ global_cooldown_seconds (int, optional): The cooldown in seconds if enabled  
                                           Required when any value of is_global_cooldown_enabled is included

+ is_paused (bool, optional): Is the reward currently paused, if true viewers cannot redeem

+ should_redemptions_skip_request_queue (bool, optional): Should redemptions be set to FULFILLED status immediately when redeemed and skip the request queue instead of the normal UNFULFILLED status

**Raises**:

+ twitchpy.errors.ClientError

**Returns**: list

### Update redemption status

~~~
function update_redemption_status(id,broadcaster_id,reward_id,status="")
~~~

Updates the status of Custom Reward Redemption objects on a channel that are in the UNFULFILLED status  
The Custom Reward Redemption specified by id must be for a Custom Reward created by the client_id attached to the user OAuth token

**Args**:

+ id (list): ID of the Custom Reward Redemption to update  
             Must match a Custom Reward Redemption on broadcaster_id’s channel  
             Maximum: 50

+ broadcaster_id (str): Provided broadcaster_id must match the user_id in the user OAuth token

+ reward_id (str): ID of the Custom Reward the redemptions to be updated are for

+ status (str, optional): The new status to set redemptions to  
                          Can be either FULFILLED or CANCELED  
                          Updating to CANCELED will refund the user their Channel Points

**Raises**:

+ twitchpy.errors.ClientError

**Returns**: list

### Get channel emotes

~~~
function get_channel_emotes(broadcaster_id)
~~~

Gets all custom emotes for a specific Twitch channel including subscriber emotes, Bits tier emotes, and follower emotes  
Custom channel emotes are custom emoticons that viewers may use in Twitch chat once they are subscribed to, cheered in, or followed the channel that owns the emotes

**Args**:

+ broadcaster_id (str): The broadcaster whose emotes are being requested

**Raises**:

+ twitchpy.errors.ClientError

**Returns**: list

### Get global emotes

~~~
function get_global_emotes()
~~~

Gets all global emotes  
Global emotes are Twitch-specific emoticons that every user can use in Twitch chat

**Raises**:

+ twitchpy.errors.ClientError

**Returns**: list

### Get emote sets

~~~
function get_emote_sets(emote_set_id)
~~~

Gets all Twitch emotes for one or more specific emote sets

**Args**:

+ emote_set_id (list): ID(s) of the emote set  
                       Maximum: 25

**Raises**:

+ twitchpy.errors.ClientError

**Returns**: list

### Get channel chat badges

~~~
function get_channel_chat_badges(broadcaster_id)
~~~

Gets a list of custom chat badges that can be used in chat for the specified channel  
This includes subscriber badges and Bit badges

**Args**:

+ broadcaster_id (str): The broadcaster whose chat badges are being requested  
                        Provided broadcaster_id must match the user_id in the user OAuth token

**Raises**:

+ twitchpy.errors.ClientError

**Returns**: list

### Get global chat badges

~~~
function get_global_chat_badges()
~~~

Gets a list of chat badges that can be used in chat for any channel

**Raises**:

+ twitchpy.errors.ClientError

**Returns**: list

### Create clip

~~~
function create_clip(broadcaster_id,has_delay=False)
~~~

This returns both an ID and an edit URL for a new clip

**Args**:

+ broadcaster_id (str): ID of the stream from which the clip will be made

+ has_delay (bool, optional): If false, the clip is captured from the live stream when the API is called; otherwise, a delay is added before the clip is captured (to account for the brief delay between the broadcaster’s stream and the viewer’s experience of that stream)  
                              Default: false

**Raises**:

+ twitchpy.errors.ClientError

**Returns**: dict

### Get clips

~~~
function get_clips(broadcaster_id="",game_id="",id=[],ended_at="",first=20,started_at="")
~~~

Gets clip information by clip ID, broadcaster ID or game ID (one only)

**Args**:

+ broadcaster_id (str, optional): ID of the broadcaster for whom clips are returned

+ game_id (str, optional): ID of the game for which clips are returned

+ id (list, optional): ID of the clip being queried  
                       Limit: 100

+ ended_at (str, optional): Ending date/time for returned clips, in RFC3339 format  
                            If this is specified, started_at also must be specified; otherwise, the time period is ignored

+ first (int, optional): Maximum number of objects to return  
                         Default: 20

+ started_at (str, optional): Starting date/time for returned clips, in RFC3339 format  
                              If this is specified, ended_at also should be specified; otherwise, the ended_at date/time will be 1 week after the started_at value

**Raises**:

+ twitchpy.errors.TooManyArgumentsError

+ twitchpy.errors.ClientError

**Returns**: list

### Get code status

~~~
function get_code_status(code,user_id)
~~~

Gets the status of one or more provided codes  
All codes are single-use

**Args**:

+ code (list): The code to get the status of
               Maximum: 20

+ user_id (int): ID of the user which is going to receive the entitlement associated with the code

**Raises**:

+ twitchpy.errors.ClientError

**Returns**: list

### Get drops entitlements

~~~
function get_drops_entitlements(id="",user_id="",game_id="",fulfillment_status="",first=20)
~~~

Gets a list of entitlements for a given organization that have been granted to a game, user, or both

**Args**:

+ id (str, optional): ID of the entitlement

+ user_id (str, optional): A Twitch User ID

+ game_id (str, optional): A Twitch Game ID

+ fulfillment_status (str, optional): An optional fulfillment status used to filter entitlements
                                      Valid values are "CLAIMED" or "FULFILLED"

+ first (int, optional): Maximum number of entitlements to return  
                         Default: 20  

**Raises**:

+ twitchpy.errors.ClientError

**Returns**: list

### Update drops entitlements

~~~
function update_drops_entitlements(entitlement_ids=[],fulfillment_status="")
~~~

Updates the fulfillment status on a set of Drops entitlements, specified by their entitlement IDs

**Args**:

+ entitlement_ids (list, optional): An array of unique identifiers of the entitlements to update  
                                    Maximum: 100

+ fulfillment_status (str, optional): A fulfillment status  
                                      Valid values are "CLAIMED" or "FULFILLED"

**Raises**:

+ twitchpy.errors.ClientError

**Returns**: list

### Redeem code

~~~
function redeem_code(code,user_id)
~~~

Redeems one or more provided codes  
All codes are single-use

**Args**:

+ code (list): The code to redeem to the authenticated user’s account  
               Maximum: 20

+ user_id (int): The user account which is going to receive the entitlement associated with the code

**Raises**:

+ twitchpy.errors.ClientError

**Returns**: list

### Create eventsub subscription

~~~
function create_eventsub_subscription(type,version,condition,transport)
~~~

Creates an EventSub subscription

**Args**:

+ type (str): The category of the subscription that is being created  
              Valid values: "channel.update", "channel.follow", "channel.subscribe", "channel.subscription.end", "channel.subscription.gift","channel.subscription.message", "channel.cheer", "channel.raid", "channel.ban", "channel.unban", "channel.moderator.add", "channel.moderator.remove", "channel.channel_points_custom_reward.add", "channel.channel_points_custom_reward.update", "channel.channel_points_custom_reward.remove", "channel.channel_points_custom_reward_redemption.add", "channel.channel_points_custom_reward_redemption.update", "channel.poll.begin", "channel.poll.progress", "channel.poll.end", "channel.prediction.begin", "channel.prediction.progress", "channel.prediction.lock", "channel.prediction.end", "drop.entitlement.grant", "extension.bits_transaction.create", "channel.hype_train.begin", "channel.hype_train.progress", "channel.hype_train.end", "stream.online", "stream.offline", "user.authorization.grant", "user.authorization.revoke", "user.update"

+ version (str): The version of the subscription type that is being created  
                 Each subscription type has independent versioning

+ condition (dict): Custom parameters for the subscription

+ transport (dict): Notification delivery specific configuration including a method string  
                    Valid transport methods include: webhook  
                    In addition to the method string, a webhook transport must include the callback and secret information

**Raises**:

+ twitchpy.errors.ClientError

**Returns**: dict

### Delete eventsub subscription

~~~
function delete_eventsub_subscription(id)
~~~

Delete an EventSub subscription

**Args**:

+ id (str): The subscription ID for the subscription to delete

### Get eventsub subscriptions

~~~
function get_eventsub_subscriptions(status="",type="")
~~~

Get a list of your EventSub subscriptions  
Only include one filter query parameter

**Args**:

+ status (str, optional): Filters subscriptions by one status type  
                          Valid values: "enabled", "webhook_callback_verification_pending", "webhook_callback_verification_failed", "notification_failures_exceeded", "authorization_revoked", "user_removed"

+ type (str, optional): Filters subscriptions by subscription type name

**Raises**:

+ twitchpy.errors.ClientError

**Returns**: list

### Get top games

~~~
function get_top_games(first=20)
~~~

Gets games sorted by number of current viewers on Twitch, most popular first

**Args**:

+ first (int, optional): Maximum number of objects to return  
                         Default: 20

**Raises**:

+ twitchpy.errors.ClientError

**Returns**: list

### Get games

~~~
function get_game(id="",name="")
~~~

Gets games by game ID or name  
For a query to be valid, name and/or id must be specified

**Args**:

+ id (list, optional): Game ID  
                          At most 100 id values can be specified

+ name (list, optional): Game name  
                         The name must be an exact match  
                         At most 100 name values can be specified

**Raises**:

+ twitchpy.errors.ClientError

**Returns**: list

### Get hype train events

~~~
function get_hype_train_events(broadcaster_id,first=1,id="")
~~~

Gets the information of the most recent Hype Train of the given channel ID  
When there is currently an active Hype Train, it returns information about that Hype Train  
When there is currently no active Hype Train, it returns information about the most recent Hype Train  
After 5 days, if no Hype Train has been active, the endpoint will return an empty response

**Args**:

+ broadcaster_id (str): User ID of the broadcaster  
                        Must match the User ID in the Bearer token if User Token is used

+ first (int, optional): Maximum number of objects to return  
                         Default: 1

+ id (str, optional): The id of the wanted event

**Raises**:

+ twitchpy.errors.ClientError

**Returns**: list

### Check automod status

~~~
function check_automod_status(broadcaster_id,msg_id,msg_user,user_id)
~~~

Determines whether a string message meets the channel’s AutoMod requirements

**Args**:

+ broadcaster_id (str): Provided broadcaster_id must match the user_id in the auth token

+ msg_id (str, optional): Developer-generated identifier for mapping messages to results

+ msg_user (str, optional): Message text

+ user_id (str, optional): User ID of the sender

**Raises**:

+ twitchpy.errors.ClientError

**Returns**: list

### Manage held automod messages

~~~
function manage_held_automod_messages(user_id,msg_id,action)
~~~

Allow or deny a message that was held for review by AutoMod

**Args**:

+ user_id (str): The moderator who is approving or rejecting the held message  
                 Must match the user_id in the user OAuth token

+ msg_id (str): ID of the message to be allowed or denied

+ action (str): The action to take for the message  
                Must be "ALLOW" or "DENY"

### Get banned events

~~~
function get_banned_events(broadcaster_id,user_id="",first=20)
~~~

Returns all user bans and un-bans in a channel

**Args**:

+ broadcaster_id (str): Provided broadcaster_id must match the user_id in the auth token

+ user_id (str, optional): Filters the results and only returns a status object for ban events that include users being banned or un-banned in this channel and have a matching user_id  
                           Maximum: 100

+ first (int, optional): Maximum number of objects to return  
                         Default: 20

**Raises**:

+ twitchpy.errors.ClientError

**Returns**: list

### Get banned users

~~~
function get_banned_users(broadcaster_id,user_id="",first=20)
~~~

Returns all banned and timed-out users in a channel

**Args**:

+ broadcaster_id (str): Provided broadcaster_id must match the user_id in the auth token

+ user_id (str, optional): Filters the results and only returns a status object for users who are banned in this channel and have a matching user_id  
                           Maximum: 100

+ first (int, optional): Maximum number of objects to return  
                         Default: 20

**Raises**:

+ twitchpy.errors.ClientError

**Returns**: list

### Get moderators

~~~
function get_moderators(broadcaster_id,user_id="",first=20)
~~~

Returns all moderators in a channel

**Args**:

+ broadcaster_id (str): Provided broadcaster_id must match the user_id in the auth token

+ user_id (str, optional): Filters the results and only returns a status object for users who are moderators in this channel and have a matching user_id  
                           Maximum: 100

+ first (int, optional): Maximum number of objects to return  
                         Default: 20

**Raises**:

+ twitchpy.errors.ClientError

**Returns**: list

### Get moderator events

~~~
function get_moderator_events(broadcaster_id,user_id="",first=20)
~~~

Returns a list of moderators or users added and removed as moderators from a channel

**Args**:

+ broadcaster_id (str): Provided broadcaster_id must match the user_id in the auth token

+ user_id (str, optional): Filters the results and only returns a status object for users who have been added or removed as moderators in this channel and have a matching user_id  
                           Maximum: 100

+ first (int, optional): Maximum number of objects to return  
                         Default: 20

**Raises**:

+ twitchpy.errors.ClientError

**Returns**: list

### Get polls

~~~
function get_polls(broadcaster_id,id="",first=20)
~~~

Get information about all polls or specific polls for a Twitch channel  
Poll information is available for 90 days

**Args**:

+ broadcaster_id (str): The broadcaster running polls  
                        Provided broadcaster_id must match the user_id in the user OAuth token

+ id (str, optional): ID of a poll  
                      Maximum: 100

+ first (int, optional): Maximum number of objects to return  
                         Default: 20

**Raises**:

+ twitchpy.errors.ClientError

**Returns**: list

### Create poll

~~~
function create_poll(broadcaster_id,title,choices,duration,bits_voting_enabled=False,bits_per_vote=0,channel_points_voting_enabled=False,channel_points_per_vote=0)
~~~

Create a poll for a specific Twitch channel

**Args**:

+ broadcaster_id (str): The broadcaster running polls  
                        Provided broadcaster_id must match the user_id in the user OAuth token

+ title (str): Question displayed for the poll  
               Maximum: 60 characters

+ choices (list): Array of the poll choices  
                  Minimum: 2 choices  
                  Maximum: 5 choices

+ duration (int): Total duration for the poll (in seconds)  
                  Minimum: 15  
                  Maximum: 1800

+ bits_voting_enabled (bool, optional): Indicates if Bits can be used for voting  
                                        Default: false

+ bits_per_vote (int, optional): Number of Bits required to vote once with Bits  
                                 Minimum: 0  
                                 Maximum: 10000

+ channel_points_voting_enabled (bool, optional): Indicates if Channel Points can be used for voting  
                                                  Default: false

+ channel_points_per_vote (int, optional): Number of Channel Points required to vote once with Channel Points  
                                           Minimum: 0  
                                           Maximum: 1000000

**Raises**:

+ twitchpy.errors.ClientError

**Returns**: dict

### End poll

~~~
function end_poll(broadcaster_id,id,status)
~~~

End a poll that is currently active

**Args**:

+ broadcaster_id (str): The broadcaster running polls  
                        Provided broadcaster_id must match the user_id in the user OAuth token

+ id (str): ID of the poll

+ status (str): The poll status to be set  
                Valid values: "TERMINATED", "ARCHIVED"

**Raises**:

+ twitchpy.errors.ClientError

**Returns**: dict

### Get predictions

~~~
function get_predictions(broadcaster_id,id="",first=20)
~~~

Get information about all Channel Points Predictions or specific Channel Points Predictions for a Twitch channel

**Args**:

+ broadcaster_id (str): The broadcaster running Predictions  
                        Provided broadcaster_id must match the user_id in the user OAuth token

+ id (str, optional): ID of a Prediction  
                      Maximum: 100

+ first (int, optional): Maximum number of objects to return  
                         Default: 20

**Raises**:

+ twitchpy.errors.ClientError

**Returns**: list

### Create prediction

~~~
function create_prediction(broadcaster_id,title,outcomes,prediction_window)
~~~

Create a Channel Points Prediction for a specific Twitch channel

**Args**:

+ broadcaster_id (str): The broadcaster running Predictions  
                        Provided broadcaster_id must match the user_id in the user OAuth token

+ title (str): Title for the Prediction  
               Maximum: 45 characters

+ outcomes (list): Array of outcome objects with titles for the Prediction  
                   Array size must be 2  
                   The first outcome object is the "blue" outcome and the second outcome object is the "pink" outcome when viewing the Prediction on Twitch

+ prediction_window (int): Total duration for the Prediction (in seconds)  
                           Minimum: 1  
                           Maximum: 1800

**Raises**:

+ twitchpy.errors.ClientError

**Returns**: dict

### End prediction

~~~
function end_prediction(broadcaster_id,id,status,winning_outcome_id="")
~~~

Lock, resolve, or cancel a Channel Points Prediction  
Active Predictions can be updated to be "locked", "resolved", or "canceled"  
Locked Predictions can be updated to be "resolved" or "canceled"

**Args**:

+ broadcaster_id (str): The broadcaster running prediction events  
                        Provided broadcaster_id must match the user_id in the user OAuth token

+ id (str): ID of the Prediction

+ status (str): The Prediction status to be set  
                Valid values: "RESOLVED", "CANCELED", "LOCKED"

+ winning_outcome_id (str, optional): ID of the winning outcome for the Prediction  
                                      This parameter is required if status is being set to RESOLVED

**Raises**:

+ twitchpy.errors.ClientError

**Returns**: dict

### Get channel stream schedule

~~~
function get_channel_stream_schedule(broadcaster_id,id="",start_time="",utc_offset="0",first=20)
~~~

Gets all scheduled broadcasts or specific scheduled broadcasts from a channel’s stream schedule  
Scheduled broadcasts are defined as "stream segments"

**Args**:

+ broadcaster_id (str): User ID of the broadcaster who owns the channel streaming schedule  
                        Provided broadcaster_id must match the user_id in the user OAuth token

+ id (str, optional): The ID of the stream segment to return  
                      Maximum: 100

+ start_time (str, optional): A timestamp in RFC3339 format to start returning stream segments from  
                              If not specified, the current date and time is used

+ utc_offset (str, optional): A timezone offset for the requester specified in minutes  
                              If not specified, "0" is used for GMT

+ first (int, optional): Maximum number of stream segments to return  
                         Default: 20

**Raises**:

+ twitchpy.errors.ClientError

**Returns**: list

### Get channel iCalendar

~~~
function get_channel_iCalendar(broadcaster_id)
~~~

Gets all scheduled broadcasts from a channel’s stream schedule as an iCalendar

**Args**:

+ broadcaster_id (str): User ID of the broadcaster who owns the channel streaming schedule

**Returns**: str

### Update channel stream schedule

~~~
function update_channel_stream_schedule(broadcaster_id,is_vacation_enabled=False,vacation_start_time="",vacation_end_time="",timezone="")
~~~

Update the settings for a channel’s stream schedule  
This can be used for setting vacation details

**Args**:

+ broadcaster_id (str): User ID of the broadcaster who owns the channel streaming schedule  
                        Provided broadcaster_id must match the user_id in the user OAuth token

+ is_vacation_enabled (bool, optional): Indicates if Vacation Mode is enabled  
                                        Set to true to add a vacation or false to remove vacation from the channel streaming schedule

+ vacation_start_time (str, optional): Start time for vacation specified in RFC3339 format  
                                       Required if is_vacation_enabled is set to true

+ vacation_end_time (str, optional): End time for vacation specified in RFC3339 format  
                                     Required if is_vacation_enabled is set to true

+ timezone (str, optional): The timezone for when the vacation is being scheduled using the IANA time zone database format  
                            Required if is_vacation_enabled is set to true

**Raises**:

+ twitchpy.errors.ClientError

**Returns**: dict

### Create channel stream schedule segment

~~~
function create_channel_stream_schedule_segment(broadcaster_id,start_time,timezone,is_recurring,duration=240,category_id="",title="")
~~~

Create a single scheduled broadcast or a recurring scheduled broadcast for a channel’s stream schedule

**Args**:

+ broadcaster_id (str): User ID of the broadcaster who owns the channel streaming schedule  
                        Provided broadcaster_id must match the user_id in the user OAuth token

+ start_time (str): Start time for the scheduled broadcast specified in RFC3339 format

+ timezone (str): The timezone of the application creating the scheduled broadcast using the IANA time zone database format

+ is_recurring (bool): Indicates if the scheduled broadcast is recurring weekly

+ duration (int, optional): Duration of the scheduled broadcast in minutes from the start_time  
                            Default: 240

+ category_id (str, optional): Game/Category ID for the scheduled broadcast

+ title (str, optional): Title for the scheduled broadcast  
                         Maximum: 140 characters

**Raises**:

+ twitchpy.errors.ClientError

**Returns**: dict

### Update channel stream schedule segment

~~~
function update_channel_stream_schedule_segment(broadcaster_id,id,start_time="",duration=240,category_id="",title="",is_canceled=False,timezone="")
~~~

Update a single scheduled broadcast or a recurring scheduled broadcast for a channel’s stream schedule

**Args**:

+ broadcaster_id (str): User ID of the broadcaster who owns the channel streaming schedule  
                        Provided broadcaster_id must match the user_id in the user OAuth token

+ id (str): The ID of the streaming segment to update

+ start_time (str, optional): Start time for the scheduled broadcast specified in RFC3339 format

+ duration (int, optional): Duration of the scheduled broadcast in minutes from the start_time  
                            Default: 240

+ category_id (str, optional): Game/Category ID for the scheduled broadcast

+ title (str, optional): Title for the scheduled broadcast  
                         Maximum: 140 characters

+ is_canceled (bool, optional): Indicated if the scheduled broadcast is canceled

+ timezone (str, optional): The timezone of the application creating the scheduled broadcast using the IANA time zone database format

**Raises**:

+ twitchpy.errors.ClientError

**Returns**: dict

### Delete channel stream schedule segment

~~~
function delete_channel_stream_schedule_segment(broadcaster_id,id)
~~~

Delete a single scheduled broadcast or a recurring scheduled broadcast for a channel’s stream schedule

**Args**:

+ broadcaster_id (str): User ID of the broadcaster who owns the channel streaming schedule  
                        Provided broadcaster_id must match the user_id in the user OAuth token

+ id (str): The ID of the streaming segment to delete

### Search categories

~~~
function search_categories(query,first=20)
~~~

Returns a list of games or categories that match the query via name either entirely or partially

**Args**:

+ query (str): URI encoded search query

+ first (int, optional): Maximum number of objects to return  
                         Default: 20

**Raises**:

+ twitchpy.errors.ClientError

**Returns**: list

### Search channels

~~~
function search_channels(query,first=20,live_only=False)
~~~

Returns a list of channels (users who have streamed within the past 6 months) that match the query via channel name or description either entirely or partially

**Args**:

+ query (str): URI encoded search query

+ first (int, optional): Maximum number of objects to return  
                         Default: 20

+ live_only (bool, optional): Filter results for live streams only  
                              Default: false

**Raises**:

+ twitchpy.errors.ClientError

**Returns**: list

### Get stream key

~~~
function get_stream_key(broadcaster_id)
~~~

Gets the channel stream key for a user

**Args**:

+ broadcaster_id (str): User ID of the broadcaster

**Raises**:

+ twitchpy.errors.ClientError

**Returns**: str

### Get streams

~~~
function get_streams(first=20,game_id="",language="",user_id="",user_login="")
~~~

Gets active streams

**Args**:

+ first (int, optional): Maximum number of objects to return  
                         Default: 20

+ game_id (str, optional): Returns streams broadcasting a specified game ID

+ language (str, optional): Stream language  
                            A language value must be either the ISO 639-1 two-letter code for a supported stream language or "other"

+ user_id (str, optional): Returns streams broadcast by one or more specified user ID

+ user_login (str, optional): Returns streams broadcast by one or more specified user login name

**Raises**:

+ twitchpy.errors.ClientError

**Returns**: list

### Get followed streams

~~~
function get_followed_streams(user_id,first=100)
~~~

Gets information about active streams belonging to channels that the authenticated user follows

**Args**:

+ user_id (str): Results will only include active streams from the channels that this Twitch user follows  
                 user_id must match the User ID in the bearer token

+ first (int, optional): Maximum number of objects to return  
                         Default: 100

**Raises**:

+ twitchpy.errors.ClientError

**Returns**: list

### Create stream marker

~~~
function create_stream_marker(user_id,description="")
~~~

Creates a marker in the stream of a user specified by user ID  
A marker is an arbitrary point in a stream that the broadcaster wants to mark; e.g., to easily return to later  
The marker is created at the current timestamp in the live broadcast when the request is processed

**Args**:

+ user_id (str): ID of the broadcaster in whose live stream the marker is created

+ description (str, optional): Description of or comments on the marker  
                               Max length is 140 characters

**Raises**:

+ twitchpy.errors.ClientError

**Returns**: list

### Get stream markers

~~~
function get_stream_markers(user_id="",video_id="",first=20)
~~~

Gets a list of markers for either a specified user’s most recent stream or a specified VOD/video (stream)  
A marker is an arbitrary point in a stream that the broadcaster wants to mark; e.g., to easily return to later  
The only markers returned are those created by the user identified by the Bearer token  
Only one of user_id and video_id must be specified

**Args**:

+ user_id (str, optional): ID of the broadcaster from whose stream markers are returned

+ video_id (str, optional): ID of the VOD/video whose stream markers are returned

+ first (int, optional): Number of values to be returned when getting videos by user or game ID  
                         Default: 20

**Raises**:

+ twitchpy.errors.ClientError

**Returns**: list

### Get broadcaster subscriptions

~~~
function get_broadcaster_subscriptions(broadcaster_id,user_id="",first=20)
~~~

Get all of a broadcaster’s subscriptions

**Args**:

+ broadcaster_id (str): User ID of the broadcaster  
                        Must match the User ID in the Bearer token

+ user_id (list, optional): Filters results to only include potential subscriptions made by the provided user ID
                            Accepts up to 100 values

+ first (int, optional): Maximum number of objects to return  
                         Default: 20

**Raises**:

+ twitchpy.errors.ClientError

**Returns**: list

### Check user subscription

~~~
function check_user_subscription(broadcaster_id,user_id)
~~~

Checks if a specific user (user_id) is subscribed to a specific channel (broadcaster_id)

**Args**:

+ broadcaster_id (str): User ID of an Affiliate or Partner broadcaster

+ user_id (str): User ID of a Twitch viewer

**Raises**:

+ twitchpy.errors.ClientError

**Returns**: dict

### Get all stream tags

~~~
function get_all_stream_tags(first=20,tag_id=[])
~~~

Gets the list of all stream tags defined by Twitch

**Args**:

+ first (int, optional): Maximum number of objects to return  
                         Default: 20

+ tag_id (list, optional): ID of a tag

**Raises**:

+ twitchpy.errors.ClientError

**Returns**: list

### Get stream tags

~~~
function get_stream_tags(broadcaster_id)
~~~

Gets the list of current stream tags that have been set for a channel

**Args**:

+ broadcaster_id (str): User ID of the channel to get tags

**Raises**:

+ twitchpy.errors.ClientError

**Returns**: list

### Replace stream tags

~~~
function replace_stream_tags(broadcaster_id,tag_ids=[])
~~~

Applies specified tags to a specified stream (channel), overwriting any existing tags applied to that stream  
If no tags are specified, all tags previously applied to the stream are removed  
Automated tags are not affected by this operation

**Args**:

+ broadcaster_id (str): ID of the stream for which tags are to be replaced

+ tag_ids (list, optional): IDs of tags to be applied to the stream

### Get channel teams

~~~
function get_channel_teams(broadcaster_id)
~~~

Retrieves a list of Twitch Teams of which the specified channel/broadcaster is a member

**Args**:

+ broadcaster_id (str): User ID for a Twitch user

**Raises**:

+ twitchpy.errors.ClientError

**Returns**: list

### Get teams

~~~
function get_teams(name="",id="")
~~~

Gets information for a specific Twitch Team  
One of the two optional query parameters must be specified to return Team information

**Args**:

+ name (str, optional): Team name

+ id (str, optional): Team ID

**Raises**:

+ twitchpy.errors.ClientError

**Returns**: Team

### Get users

~~~
function get_users(id=[],login=[])
~~~

Gets an user  
Users are identified by optional user IDs and/or login name  
If neither a user ID nor a login name is specified, the user is looked up by Bearer token

**Args**:

+ id (list, optional): User ID  
                       Limit: 100

+ login (list, optional): User login name  
                          Limit: 100

**Raises**:

+ twitchpy.errors.ClientError

**Returns**: list

### Update user

~~~
function update_user(description="")
~~~

Updates the description of a user specified by the bearer token  
If the description parameter is not provided, no update will occur and the current user data is returned

**Args**:

+ description (str, optional): User’s account description

**Raises**:

+ twitchpy.errors.ClientError

**Returns**: User

### Get user follows

~~~
function get_user_follows(first=20,from_id="",to_id="")
~~~

Gets information on follow relationships between Twitch users  
At minimum, from_id or to_id must be provided for a query to be valid

**Args**:

+ first (int, optional): Maximum number of objects to return  
                         Default: 20

+ from_id (str, optional): User ID  
                           The request returns information about users who are being followed by the from_id user

+ to_id (str, optional): User ID  
                         The request returns information about users who are following the to_id user

**Raises**:

+ twitchpy.errors.ClientError

**Returns**: list

### Get user block list

~~~
function get_user_block_list(broadcaster_id,first=20)
~~~

Gets a specified user’s block list

**Args**:

+ broadcaster_id (str): User ID for a Twitch user

+ first (int, optional): Maximum number of objects to return  
                         Default: 20

**Raises**:

+ twitchpy.errors.ClientError

**Returns**: list

### Block user

~~~
function block_user(target_user_id,source_context="",reason="")
~~~

Blocks the specified user on behalf of the authenticated user

**Args**:

+ target_user_id (str): User ID of the user to be blocked

+ source_context (str, optional): Source context for blocking the user  
                                  Valid values: "chat", "whisper"

+ reason (str, optional): Reason for blocking the user  
                          Valid values: "spam", "harassment", or "other"

### Unblock user

~~~
function unblock_user(target_user_id)
~~~

Unblocks the specified user on behalf of the authenticated user

**Args**:

+ target_user_id (str): User ID of the user to be unblocked

### Get user extensions

~~~
function get_user_extensions():
~~~

Gets a list of all extensions (both active and inactive) for a specified user, identified by a Bearer token

**Raises**:

+ twitchpy.errors.ClientError

**Returns**: list

### Get user active extensions

~~~
function get_user_active_extensions(user_id="")
~~~

Gets information about active extensions installed by a specified user, identified by a user ID or Bearer token

**Args**:

+ user_id (str, optional): ID of the user whose installed extensions will be returned

**Raises**:

+ twitchpy.errors.ClientError

**Returns**: list

### Update user extensions

~~~
function update_user_extensions()
~~~

Updates the activation state, extension ID, and/or version number of installed extensions for a specified user, identified by a Bearer token  
If you try to activate a given extension under multiple extension types, the last write wins (and there is no guarantee of write order)

**Raises**:

+ twitchpy.errors.ClientError

**Returns**: list

### Get videos

~~~
function get_videos(id,user_id,game_id,first=20,language="",period="all",sort="time",type="all")
~~~

Gets video information by video ID, user ID, or game ID  
Each request must specify one video id, one user_id, or one game_id

**Args**:

+ id (list): ID of the video being queried  
             Limit: 100  
             If this is specified, you cannot use first, language, period, sort and type

+ user_id (str): ID of the user who owns the video

+ game_id (str): ID of the game the video is of

+ first (int, optional): Number of values to be returned when getting videos by user or game ID  
                         Default: 20

+ language (str, optional): Language of the video being queried  
                            A language value must be either the ISO 639-1 two-letter code for a supported stream language or "other"

+ period (str, optional): Period during which the video was created  
                          Valid values: "all", "day", "week", "month"

+ sort (str, optional): Sort order of the videos  
                        Valid values: "time", "trending", "views"  
                        Default: "time"

+ type (str, optional): Type of video  
                        Valid values: "all", "upload", "archive", "highlight"  
                        Default: "all"

**Raises**:

+ twitchpy.errors.ClientError

**Returns**: list

### Delete video

~~~
function delete_video(id)
~~~

Deletes a video  
Videos are past broadcasts, Highlights, or uploads

**Args**:

id (str): ID of the video to be deleted  
          Limit: 5

### Get webhook subscriptions

~~~
function get_webhook_subscriptions(first=20)
~~~

Gets the Webhook subscriptions of an application identified by a Bearer token, in order of expiration

**Args**:

+ first (int, optional): Number of values to be returned  
                         Limit: 100  
                         Default: 20

**Raises**:

+ twitchpy.errors.ClientError

**Returns**: list

### Get chatters

~~~
function get_chatters(channel_name)
~~~

Gets all users in a chat

**Args**:

+ channel_name (str): Name of the user who is owner of the chat

**Raises**:

+ twitchpy.errors.ClientError

**Returns**: list

## Channel

~~~
class Channel(oauth_token,client_id,client_secret,name,game_name,broadcaster_language,title)
~~~

Represents a channel

**Args**:

+ oauth_token (str): OAuth token to identify the application

+ client_id (str): Client ID to identify the application

+ client_secret (str): Client secret to identify the application

+ name (str): Channel's name

+ game_name (str): Channel's category's name

+ broadcaster_language (str): Channel's language

+ title (str): Title in the channel

### Connect

~~~
function connect()
~~~

Creates a connection with the channel

### Send

~~~
function send(text)
~~~

Sends a message by chat

**Args**:

+ text (str): Message's text

### Ban

~~~
function ban(username,reason="")
~~~

Bans a user

**Args**:

+ username (str): User to ban

+ reason (str, optional): Reason of the ban

### Unban

~~~
function unban(username)
~~~

Undoes the ban of a user

**Args**:

+ username (str): Name of the user to readmit

### Clear

~~~
function clear()
~~~

Clears the chat

### Delete poll

~~~
function delete_poll()
~~~

Eliminates the active poll

### Emoteonly

~~~
function emoteonly()
~~~

Activates the "emotes only" mode

### Emoteonly off

~~~
function emoteonly_off()
~~~

Disables "emotes only" mode

### End poll

~~~
function end_poll()
~~~

Finish the active poll

### Followers

~~~
function followers(duration="0m")
~~~

Activates the "followers only" mode

**Args**:

+ duration (str, optional): Follow-up duration

### Followers off

~~~
function followers_off()
~~~

Disables the "followers only" mode

### Host

~~~
function host(channel)
~~~

Hosts a channel

**Args**:

channel (str): Name of the channel to host

### Unhost

~~~
function unhost()
~~~

Unhosts the hosted channel

### Marker

~~~
function marker(description="")
~~~

Leaves a mark on the channel's stream

**Args**:

+ description (str, optional): Mark's description

### Mod

~~~
function mod(username)
~~~

Makes a user mod

**Args**:

+ username (str): Name of the user to be promoted

### Unmod

~~~
function unmod(username)
~~~

Removes the moderator's rank from a user

**Args**:

+ username (str): User's name

### Poll

~~~
function poll()
~~~

Opens a configuration menu for creating a poll

### Prediction

~~~
function prediction()
~~~

Opens a configuration menu for creating a prediction

### Raid

~~~
function raid(channel)
~~~

Raids another channel

**Args**:

+ channel (str): Name of the channel to raid

### Unraid

~~~
function unraid()
~~~

Cancels a raid

### Requests

~~~
function requests()
~~~

Opens the reward requests queue

### Slow

~~~
function slow(duration)
~~~

Activates the "slow" mode

**Args**:

+ duration (int): Time between messages

### Slow off

~~~
function slow_off()
~~~

Disables the "slow" mode

### Subscribers

~~~
function subscribers()
~~~

Activates the "subscribers only" mode

### Subscribers off

~~~
function subscribers_off()
~~~

Disables "subscriber only" mode

### Timeout

~~~
function timeout(username,duration=600,reason="")
~~~

Expels a user temporarily

**Args**:

+ username (str): Name of the user to expel

+ duration (int, optional): Ejecting time

+ reason (str, optional): Reason for expulsion

### Untimeout

~~~
function untimeout(username)
~~~

Cancels the timeout of a user

**Args**:

+ username (str): User to readmit

### Uniquechat

~~~
function uniquechat()
~~~

Activates the "unique" mode

### Uniquechat off

~~~
function uniquechat_off()
~~~

Disables the "unique" mode

### User

~~~
function user(username)
~~~

Shows information about a user

**Args**:

+ username (str): User to show information about

### Vip

~~~
function vip(username)
~~~

Makes a user vip

**Args**:

+ username (str): User's name

### Unvip

~~~
function unvip(username)
~~~

Removes the vip range from a user

**Args**:

+ username (str): User's name

### Block

~~~
function block(username)
~~~

Blocks a user

**Args**:

+ username (str): User to block

### Unblock

~~~
function unblock(username)
~~~

Unblocks a user

**Args**:

+ username (str): Name of the user to unblock

### Color

~~~
function color(color)
~~~

Changes the color of the channel's name in the chat

**Args**:

+ color (str): New color's name

### Help

~~~
function help(command)
~~~

Shows detailed information about a command

**Args**:

+ command (str): Command to show information about

### Me

~~~
function me(text)
~~~

Sends a message by chat with the color of the channel's name

**Args**:

+ text (str): Message' text

### Mods

~~~
function mods()
~~~

Shows the moderators list of the channel

### Vips

~~~
function vips()
~~~

Shows the vips list of the channel

### Vote

~~~
function vote(index)
~~~

Votes in the active poll

**Args**:

+ index (int): Number of the option

### Commercial

~~~
function commercial(duration=30)
~~~

Places advertising in the channel

**Args**:

+ duration (int, optional): Duration of advertising

### Whisper

~~~
function whisper(username,text)
~~~

Whispers to a user

**Args**:

+ username (str): User's name

+ text (str): Whisper's text

## Bot

~~~
class Bot(oauth_token,client_id,client_secret,username,channels,command_prefix,code="",ready_message="")
~~~

**Args**:

+ oauth_token (str): OAuth token

+ client_id (str): Client ID

+ client_secret (str): Client secret

+ username (str): Name of the bot

+ channels (list): Names of channels the bot will access

+ command_prefix (str): Prefix of the commands the bot will recognize

+ code (str, optional): Authorization code

+ ready_message (str, optional): Message that the bot will send through the chats of the channels it access

### Run

~~~
function run()
~~~

Runs the bot

### Add check

~~~
function add_check(name,check)
~~~

Adds a check to the bot  
Checks work permanently

**Args**:

+ name (str): Check's name

+ check (func): Method that will act as a check

### Add listener

~~~
function add_listener(name,listener)
~~~

Adds a command to the bot  
Listeners work only when a message is received
Listeners must receive as a parameter the last message in the chat

**Args**:

+ name (str): Command's name

+ listener (str): Method that will be executed when the command is invoked

### Add command

~~~
function add_command(name,command)
~~~

Adds a command to the bot
Commands must receive as a parameter the messages which call them

**Args**:

+ name (str): Command's name

+ command (func): Method that will be executed when the command is invoked

### Start commercial

~~~
function start_commercial(broadcaster_id,length)
~~~

Starts a commercial on a specified channel

**Args**:

+ broadcaster_id (int): ID of the channel requesting a commercial

+ length (int): Desired length of the commercial in seconds  
                Valid options are 30, 60, 90, 120, 150 and 180

**Returns**: list

### Get extension analytics

~~~
function get_extension_analytics(ended_at="",extension_id="",first=20,started_at="",type="")
~~~

Gets a URL that Extension developers can use to download analytics reports for their Extensions  
The URL is valid for 5 minutes

**Args**:

+ ended_at (str, optional): Ending date/time for returned reports, in RFC3339 format with the hours, minutes, and seconds zeroed out and the UTC timezone: YYYY-MM-DDT00:00:00Z  
                            If this is provided, started_at also must be specified

+ extension_id (str, optional): Client ID value assigned to the extension when it is created

+ first (int, optional): Maximum number of objects to return  
                         Default: 20

+ started_at (str, optional): Starting date/time for returned reports, in RFC3339 format with the hours, minutes, and seconds zeroed out and the UTC timezone: YYYY-MM-DDT00:00:00Z  
                              This must be on or after January 31, 2018  
                              If this is provided, ended_at also must be specified

+ type (str, optional): Type of analytics report that is returned  
                        Valid values: "overview_v2"

**Returns**: list

### Get game analytics

~~~
function get_game_analytics(ended_at="",first=20,game_id="",started_at="",type="")
~~~

Gets a URL that game developers can use to download analytics reports for their games  
The URL is valid for 5 minutes

**Args**:

+ ended_at (str, optional): Ending date/time for returned reports, in RFC3339 format with the hours, minutes, and seconds zeroed out and the UTC timezone: YYYY-MM-DDT00:00:00Z  
                            If this is provided, started_at also must be specified

+ first (int, optional): Maximum number of objects to return  
                         Default: 20

+ game_id (str, optional): Game ID

+ started_at (str, optional): Starting date/time for returned reports, in RFC3339 format with the hours, minutes, and seconds zeroed out and the UTC timezone: YYYY-MM-DDT00:00:00Z  
                              If this is provided, ended_at also must be specified

+ type (str, optional): Type of analytics report that is returned  
                        Valid values: "overview_v2"

**Returns**: list

### Get bits leaderboard

~~~
function get_bits_leaderboard(count=10,user_id="")
~~~

Gets a ranked list of Bits leaderboard information for a broadcaster

**Args**:

+ count (int, optional): Number of results to be returned  
                         Maximum: 100  
                         Default: 10

+ period (str, optional): Time period over which data is aggregated (PST time zone)  
                          This parameter interacts with started_at  
                          Default: "all"  
                          Valid values: "day", "week", "month", "year", "all"

+ started_at (str, optional): Timestamp for the period over which the returned data is aggregated  
                              Must be in RFC 3339 format  
                              This value is ignored if period is "all"

+ user_id (str, optional): ID of the user whose results are returned  
                           As long as count is greater than 1, the returned data includes additional users, with Bits amounts above and below the user specified


**Returns**: list

### Get cheermotes

~~~
function get_cheermotes(broadcaster_id="")
~~~

Retrieves the list of available Cheermotes  
Cheermotes returned are available throughout Twitch, in all Bits-enabled channels

**Args**:

+ broadcaster_id (str, optional): ID for the broadcaster who might own specialized Cheermotes

**Returns**: list

### Get extension transactions

~~~
function get_extension_transactions(extension_id,id=[],first=20)
~~~

Allows extension back end servers to fetch a list of transactions that have occurred for their extension across all of Twitch  
A transaction is a record of a user exchanging Bits for an in-Extension digital good

**Args**:

+ extension_id (str): ID of the extension to list transactions for

+ id (list, optional): Transaction IDs to look up  
                       Maximum: 100

+ first (int, optional): Maximum number of objects to return  
                         Default: 20

**Returns**: list

### Get channel

~~~
function get_channel(broadcaster_id)
~~~

Gets a channel

**Args**:

+ broadcaster_id (str): ID of the channel to be updated

**Returns**: Channel

### Modify channel information

~~~
function modify_channel_information(broadcaster_id,game_id="",broadcaster_language="",title="")
~~~

Modifies channel information for users  
game_id, broadcaster_language, title and delay parameters are optional, but at least one parameter must be provided

**Args**:

+ broadcaster_id (str): ID of the channel to be updated

+ game_id (str, optional): The current game ID being played on the channel

+ broadcaster_language (str, optional): The language of the channel  
                                        A language value must be either the ISO 639-1 two-letter code for a supported stream language or “other”

+ title (str, optional): The title of the stream

+ delay (int ,optional): Stream delay in seconds  
                         Stream delay is a Twitch Partner feature

### Get channel editors

~~~
function get_channel_editors(broadcaster_id)
~~~

Gets a list of users who have editor permissions for a specific channel

**Args**:

+ broadcaster_id (str): Broadcaster’s user ID associated with the channel

**Returns**: list

### Create custom reward

~~~
function create_custom_reward(broadcaster_id,title,cost,prompt="",is_enabled=True,background_color="",is_user_input_required=False,is_max_per_stream_enabled=False,max_per_stream=None,is_max_per_user_per_stream_enabled=False,max_per_user_per_stream=None,is_global_cooldown_enabled=False,global_cooldown_seconds=None,should_redemptions_skip_request_queue=False)
~~~

Creates a Custom Reward on a channel

**Args**:

+ broadcaster_id (str): ID of the channel creating a reward

+ title (str): The title of the reward

+ cost (int): The cost of the reward

+ prompt (str, optional): The prompt for the viewer when they are redeeming the reward

+ is_enabled (bool, optional): Is the reward currently enabled, if false the reward won’t show up to viewers  
                               Default: true

+ background_color (str, optional): Custom background color for the reward  
                                    Format: Hex with # prefix

+ is_user_input_required (bool, optional): Does the user need to enter information when redeeming the reward  
                                           Default: false

+ is_max_per_stream_enabled (bool, optional): Whether a maximum per stream is enabled  
                                              Default: false

+ max_per_stream (int, optional): The maximum number per stream if enabled  
                                  Required when any value of is_max_per_stream_enabled is included

+ is_max_per_user_per_stream_enabled (bool, optional): Whether a maximum per user per stream is enabled  
                                                       Default: false

+ max_per_user_per_stream (int, optional): The maximum number per user per stream if enabled  
                                           Required when any value of is_max_per_user_per_stream_enabled is included

+ is_global_cooldown_enabled (bool, optional): Whether a cooldown is enabled  
                                               Default: false

+ global_cooldown_seconds (int, optional): The cooldown in seconds if enabled  
                                           Required when any value of is_global_cooldown_enabled is included

+ should_redemptions_skip_request_queue (bool, optional): Should redemptions be set to FULFILLED status immediately when redeemed and skip the request queue instead of the normal UNFULFILLED status  
                                                          Default: false

**Returns**: list

### Delete custom reward

~~~
function delete_custom_reward(broadcaster_id,id)
~~~

Deletes a Custom Reward on a channel  
The Custom Reward specified by id must have been created by the client_id attached to the OAuth token in order to be deleted  
Any UNFULFILLED Custom Reward Redemptions of the deleted Custom Reward will be updated to the FULFILLED status

**Args**:

+ broadcaster_id (str): Provided broadcaster_id must match the user_id in the user OAuth token

+ id (str): ID of the Custom Reward to delete  
            Must match a Custom Reward on broadcaster_id’s channel

### Get custom reward

~~~
function get_custom_reward(broadcaster_id,id=[],only_manageable_rewards=False)
~~~

Returns a list of Custom Reward objects for the Custom Rewards on a channel

**Args**:

+ broadcaster_id (str): Provided broadcaster_id must match the user_id in the user OAuth token

+ id (list, optional): This parameter filters the results and only returns reward objects for the Custom Rewards with matching ID  
                       Maximum: 50

+ only_manageable_rewards (bool, optional): When set to true, only returns custom rewards that the calling broadcaster can manage  
                                            Default: false

**Returns**: list

### Get custom reward redemption

~~~
function get_custom_reward_redemption(broadcaster_id,reward_id,id=[],status="",sort="OLDEST",first=20)
~~~

Returns Custom Reward Redemption objects for a Custom Reward on a channel that was created by the same client_id  
Developers only have access to get and update redemptions for the rewards created programmatically by the same client_id

**Args**:

+ broadcaster_id (str): Provided broadcaster_id must match the user_id in the user OAuth token

+ reward_id (str): When ID is not provided, this parameter returns Custom Reward Redemption objects for redemptions of the Custom Reward with ID reward_id

+ id (list, optional): When id is not provided, this param filters the results and only returns Custom Reward Redemption objects for the redemptions with matching ID  
                       Maximum: 50

+ status (str, optional): This param filters the Custom Reward Redemption objects for redemptions with the matching status  
                          Can be one of UNFULFILLED, FULFILLED or CANCELED

+ sort (str, optional): Sort order of redemptions returned when getting the Custom Reward Redemption objects for a reward  
                        One of: OLDEST, NEWEST  
                        Default: OLDEST

+ first (int, optional): Number of results to be returned when getting the Custom Reward Redemption objects for a reward  
                         Default: 20

**Returns**: list

### Update custom reward

~~~
function update_custom_reward(broadcaster_id,id,title="",prompt="",cost=None,background_color="",is_enabled=None,is_user_input_required=None,is_max_per_stream_enabled=None,max_per_stream=None,is_max_per_user_per_stream_enabled=False,max_per_user_per_stream=None,is_global_cooldown_enabled=False,global_cooldown_seconds=None,is_paused=None,should_redemptions_skip_request_queue=None)
~~~

Updates a Custom Reward created on a channel  
The Custom Reward specified by id must have been created by the client_id attached to the user OAuth token

**Args**:

+ broadcaster_id (str): Provided broadcaster_id must match the user_id in the user OAuth token

+ id (str): ID of the Custom Reward to update  
            Must match a Custom Reward on the channel of the broadcaster_id

+ title (str, optional): The title of the reward

+ prompt (str, optional): The prompt for the viewer when they are redeeming the reward

+ cost (int, optional): The cost of the reward

+ background_color (str, optional): Custom background color for the reward as a hexadecimal value

+ is_enabled (bool, optional): Is the reward currently enabled, if false the reward won’t show up to viewers

+ is_user_input_required (bool, optional): Does the user need to enter information when redeeming the reward

+ is_max_per_stream_enabled (bool, optional): Whether a maximum per stream is enabled  
                                              Required when any value of max_per_stream is included

+ max_per_stream (int, optional): The maximum number per stream if enabled  
                                  Required when any value of is_max_per_stream_enabled is included

+ is_max_per_user_per_stream_enabled (bool, optional): Whether a maximum per user per stream is enabled  
                                                       Required when any value of max_per_user_per_stream is included

+ max_per_user_per_stream (int, optional): The maximum number per user per stream if enabled  
                                           Required when any value of is_max_per_user_per_stream_enabled is included

+ is_global_cooldown_enabled (bool, optional): Whether a cooldown is enabled  
                                               Required when any value of global_cooldown_seconds is included

+ global_cooldown_seconds (int, optional): The cooldown in seconds if enabled  
                                           Required when any value of is_global_cooldown_enabled is included

+ is_paused (bool, optional): Is the reward currently paused, if true viewers cannot redeem

+ should_redemptions_skip_request_queue (bool, optional): Should redemptions be set to FULFILLED status immediately when redeemed and skip the request queue instead of the normal UNFULFILLED status

**Returns**: list

### Update redemption status

~~~
function update_redemption_status(id,broadcaster_id,reward_id,status="")
~~~

Updates the status of Custom Reward Redemption objects on a channel that are in the UNFULFILLED status  
The Custom Reward Redemption specified by id must be for a Custom Reward created by the client_id attached to the user OAuth token

**Args**:

id (list): ID of the Custom Reward Redemption to update  
           Must match a Custom Reward Redemption on broadcaster_id’s channel  
           Maximum: 50

+ broadcaster_id (str): Provided broadcaster_id must match the user_id in the user OAuth token

+ reward_id (str): ID of the Custom Reward the redemptions to be updated are for

+ status (str, optional): The new status to set redemptions to  
                          Can be either FULFILLED or CANCELED  
                          Updating to CANCELED will refund the user their Channel Points

**Returns**: list

### Get channel emotes

~~~
function get_channel_emotes(broadcaster_id)
~~~

Gets all custom emotes for a specific Twitch channel including subscriber emotes, Bits tier emotes, and follower emotes  
Custom channel emotes are custom emoticons that viewers may use in Twitch chat once they are subscribed to, cheered in, or followed the channel that owns the emotes

**Args**:

+ broadcaster_id (str): The broadcaster whose emotes are being requested

**Returns**: list

### Get global emotes

~~~
function get_global_emotes()
~~~

Gets all global emotes  
Global emotes are Twitch-specific emoticons that every user can use in Twitch chat

**Returns**: list

### Get emote sets

~~~
function get_emote_sets(emote_set_id)
~~~

Gets all Twitch emotes for one or more specific emote sets

**Args**:

+ emote_set_id (list): ID(s) of the emote set  
                       Maximum: 25

**Returns**: list

### Get channel chat badges

~~~
function get_channel_chat_badges(broadcaster_id)
~~~

Gets a list of custom chat badges that can be used in chat for the specified channel  
This includes subscriber badges and Bit badges

**Args**:

+ broadcaster_id (str): The broadcaster whose chat badges are being requested  
                        Provided broadcaster_id must match the user_id in the user OAuth token

**Returns**: list

### Get global chat badges

~~~
function get_global_chat_badges()
~~~

Gets a list of chat badges that can be used in chat for any channel

**Returns**: list

### Create clip

~~~
function create_clip(broadcaster_id,has_delay=False)
~~~

This returns both an ID and an edit URL for a new clip

**Args**:

+ broadcaster_id (str): ID of the stream from which the clip will be made

+ has_delay (bool, optional): If false, the clip is captured from the live stream when the API is called; otherwise, a delay is added before the clip is captured (to account for the brief delay between the broadcaster’s stream and the viewer’s experience of that stream)  
                              Default: false

**Returns**: dict

### Get clips

~~~
function get_clips(broadcaster_id="",game_id="",id=[],ended_at="",first=20,started_at="")
~~~

Gets clip information by clip ID, broadcaster ID or game ID (one only)

**Args**:

+ broadcaster_id (str, optional): ID of the broadcaster for whom clips are returned

+ game_id (str, optional): ID of the game for which clips are returned

+ id (list, optional): ID of the clip being queried  
                       Limit: 100

+ ended_at (str, optional): Ending date/time for returned clips, in RFC3339 format  
                            If this is specified, started_at also must be specified; otherwise, the time period is ignored

+ first (int, optional): Maximum number of objects to return  
                         Default: 20

+ started_at (str, optional): Starting date/time for returned clips, in RFC3339 format  
                              If this is specified, ended_at also should be specified; otherwise, the ended_at date/time will be 1 week after the started_at value

**Returns**: list

### Get code status

~~~
function get_code_status(code,user_id)
~~~

Gets the status of one or more provided codes  
All codes are single-use

**Args**:

+ code (list): The code to get the status of  
               Maximum: 20

+ user_id (int): The user account which is going to receive the entitlement associated with the code

**Returns**: list

### Get drops entitlements

~~~
function get_drops_entitlements(id="",user_id="",game_id="",fulfillment_status="",first=20)
~~~

Gets a list of entitlements for a given organization that have been granted to a game, user, or both

**Args**:

+ id (str, optional): ID of the entitlement

+ user_id (str, optional): A Twitch User ID

+ game_id (str, optional): A Twitch Game ID

+ fulfillment_status (str, optional): An optional fulfillment status used to filter entitlements
                                      Valid values are "CLAIMED" or "FULFILLED"

+ first (int, optional): Maximum number of entitlements to return  
                         Default: 20

**Returns**: list

### Update drops entitlements

~~~
function update_drops_entitlements(entitlement_ids=[],fulfillment_status="")
~~~

Updates the fulfillment status on a set of Drops entitlements, specified by their entitlement IDs

**Args**:

+ entitlement_ids (list, optional): An array of unique identifiers of the entitlements to update  
                                    Maximum: 100

+ fulfillment_status (str, optional): A fulfillment status  
                                      Valid values are "CLAIMED" or "FULFILLED"

**Returns**: list

### Redeem code

~~~
function redeem_code(code,user_id)
~~~

Redeems one or more provided codes  
All codes are single-use

**Args**:

+ code (list): The code to redeem to the authenticated user’s account  
               Maximum: 20

+ user_id (int): The user account which is going to receive the entitlement associated with the code

**Returns**: list

### Create eventsub subscription

~~~
function create_eventsub_subscription(type,version,condition,transport)
~~~

Creates an EventSub subscription

**Args**:

+ type (str): The category of the subscription that is being created  
              Valid values: "channel.update", "channel.follow", "channel.subscribe", "channel.subscription.end", "channel.subscription.gift","channel.subscription.message", "channel.cheer", "channel.raid", "channel.ban", "channel.unban", "channel.moderator.add", "channel.moderator.remove", "channel.channel_points_custom_reward.add", "channel.channel_points_custom_reward.update", "channel.channel_points_custom_reward.remove", "channel.channel_points_custom_reward_redemption.add", "channel.channel_points_custom_reward_redemption.update", "channel.poll.begin", "channel.poll.progress", "channel.poll.end", "channel.prediction.begin", "channel.prediction.progress", "channel.prediction.lock", "channel.prediction.end", "drop.entitlement.grant", "extension.bits_transaction.create", "channel.hype_train.begin", "channel.hype_train.progress", "channel.hype_train.end", "stream.online", "stream.offline", "user.authorization.grant", "user.authorization.revoke", "user.update"

+ version (str): The version of the subscription type that is being created  
                 Each subscription type has independent versioning

+ condition (dict): Custom parameters for the subscription

+ transport (dict): Notification delivery specific configuration including a method string  
                    Valid transport methods include: webhook  
                    In addition to the method string, a webhook transport must include the callback and secret information

**Returns**: dict

### Delete eventsub subscription

~~~
function delete_eventsub_subscription(id)
~~~

Delete an EventSub subscription

**Args**:

+ id (str): The subscription ID for the subscription to delete

### Get eventsub subscriptions

~~~
function get_eventsub_subscriptions(status="",type="")
~~~

Get a list of your EventSub subscriptions  
Only include one filter query parameter

**Args**:

+ status (str, optional): Filters subscriptions by one status type  
                          Valid values: "enabled", "webhook_callback_verification_pending", "webhook_callback_verification_failed", "notification_failures_exceeded", "authorization_revoked", "user_removed"

+ type (str, optional): Filters subscriptions by subscription type name

**Returns**: list

### Get top games

~~~
function get_top_games(first=20)
~~~

Gets games sorted by number of current viewers on Twitch, most popular first

**Args**:

+ first (int, optional): Maximum number of objects to return  
                         Default: 20

**Returns**: list

### Get games

~~~
function get_games(self,id=[],name=[])
~~~

Gets games by game ID or name  
For a query to be valid, name and/or id must be specified

**Args**:

+ id (list, optional): Game ID  
                       At most 100 id values can be specified

+ name (list, optional): Game name  
                         The name must be an exact match  
                         At most 100 name values can be specified

**Returns**: list

### Get hype train events

~~~
function get_hype_train_events(broadcaster_id,first=1,id="")
~~~

Gets the information of the most recent Hype Train of the given channel ID  
When there is currently an active Hype Train, it returns information about that Hype Train  
When there is currently no active Hype Train, it returns information about the most recent Hype Train  
After 5 days, if no Hype Train has been active, the endpoint will return an empty response

**Args**:

+ broadcaster_id (str): User ID of the broadcaster  
                        Must match the User ID in the Bearer token if User Token is used

+ first (int, optional): Maximum number of objects to return  
                         Default: 1

+ id (str, optional): The id of the wanted event

**Returns**: list

### Check automod status

~~~
function check_automod_status(broadcaster_id,msg_id,msg_user,user_id)
~~~

Determines whether a string message meets the channel’s AutoMod requirements

**Args**:

+ broadcaster_id (str): Provided broadcaster_id must match the user_id in the auth token

+ msg_id (str, optional): Developer-generated identifier for mapping messages to results

+ msg_user (str, optional): Message text

+ user_id (str, optional): User ID of the sender

**Returns**: list

### Manage held automod messages

~~~
function manage_held_automod_messages(user_id,msg_id,action)
~~~

Allow or deny a message that was held for review by AutoMod

**Args**:

+ user_id (str): The moderator who is approving or rejecting the held message  
                 Must match the user_id in the user OAuth token

+ msg_id (str): ID of the message to be allowed or denied

+ action (str): The action to take for the message  
                Must be "ALLOW" or "DENY"

### Get banned events

~~~
function get_banned_events(broadcaster_id,user_id="",first=20)
~~~

Returns all user bans and un-bans in a channel

**Args**:

+ broadcaster_id (str): Provided broadcaster_id must match the user_id in the auth token

+ user_id (list, optional): Filters the results and only returns a status object for ban events that include users being banned or un-banned in this channel and have a matching user_id  
                            Maximum: 100

+ first (int, optional): Maximum number of objects to return  
                         Default: 20

**Returns**: list

### Get banned users

~~~
function get_banned_users(broadcaster_id,user_id="",first=20)
~~~

Returns all banned and timed-out users in a channel

**Args**:

+ broadcaster_id (str): Provided broadcaster_id must match the user_id in the auth token

+ user_id (list, optional): Filters the results and only returns a status object for users who are banned in this channel and have a matching user_id  
                            Maximum: 100

+ first (int, optional): Maximum number of objects to return  
                         Default: 20

**Returns**: list

### Get moderators

~~~
function get_moderators(broadcaster_id,user_id="",first=20)
~~~

Returns all moderators in a channel

**Args**:

+ broadcaster_id (str): Provided broadcaster_id must match the user_id in the auth token

+ user_id (list, optional): Filters the results and only returns a status object for users who are moderators in this channel and have a matching user_id  
                            Maximum: 100

+ first (int, optional): Maximum number of objects to return  
                         Default: 20

**Returns**: list

### Get moderator events

~~~
function get_moderator_events(broadcaster_id,user_id="",first=20)
~~~

Returns a list of moderators or users added and removed as moderators from a channel

**Args**:

+ broadcaster_id (str): Provided broadcaster_id must match the user_id in the auth token

+ user_id (list, optional): Filters the results and only returns a status object for users who have been added or removed as moderators in this channel and have a matching user_id  
                            Maximum: 100

+ first (int, optional): Maximum number of objects to return
                         Default: 20

**Returns**: list

### Get polls

~~~
function get_polls(broadcaster_id,id=[],first=20)
~~~

Get information about all polls or specific polls for a Twitch channel  
Poll information is available for 90 days

**Args**:

+ broadcaster_id (str): The broadcaster running polls  
                        Provided broadcaster_id must match the user_id in the user OAuth token

+ id (list, optional): ID of a poll  
                       Maximum: 100

+ first (int, optional): Maximum number of objects to return  
                         Default: 20

**Returns**: list

### Create poll

~~~
function create_poll(broadcaster_id,title,choices,duration,bits_voting_enabled=False,bits_per_vote=0,channel_points_voting_enabled=False,channel_points_per_vote=0)
~~~

Create a poll for a specific Twitch channel

**Args**:

+ broadcaster_id (str): The broadcaster running polls  
                        Provided broadcaster_id must match the user_id in the user OAuth token

+ title (str): Question displayed for the poll  
               Maximum: 60 characters

+ choices (list): Array of the poll choices  
                  Minimum: 2 choices  
                  Maximum: 5 choices

+ duration (int): Total duration for the poll (in seconds)  
                  Minimum: 15  
                  Maximum: 1800

+ bits_voting_enabled (bool, optional): Indicates if Bits can be used for voting  
                                        Default: false

+ bits_per_vote (int, optional): Number of Bits required to vote once with Bits  
                                 Minimum: 0  
                                 Maximum: 10000

+ channel_points_voting_enabled (bool, optional): Indicates if Channel Points can be used for voting  
                                                  Default: false

+ channel_points_per_vote (int, optional): Number of Channel Points required to vote once with Channel Points  
                                           Minimum: 0  
                                           Maximum: 1000000

**Returns**: dict

### End poll

~~~
function end_poll(broadcaster_id,id,status)
~~~

End a poll that is currently active

**Args**:

+ broadcaster_id (str): The broadcaster running polls  
                        Provided broadcaster_id must match the user_id in the user OAuth token

+ id (str): ID of the poll

+ status (str): The poll status to be set  
                Valid values: "TERMINATED", "ARCHIVED"

**Returns**: dict

### Get predictions

~~~
function get_predictions(broadcaster_id,id=[],first=20)
~~~

Get information about all Channel Points Predictions or specific Channel Points Predictions for a Twitch channel

**Args**:

+ broadcaster_id (str): The broadcaster running Predictions  
                        Provided broadcaster_id must match the user_id in the user OAuth token

+ id (str, optional): ID of a Prediction  
                      Maximum: 100

+ first (int, optional): Maximum number of objects to return  
                         Default: 20

**Returns**: list

### Create prediction

~~~
function create_prediction(broadcaster_id,title,outcomes,prediction_window)
~~~

Create a Channel Points Prediction for a specific Twitch channel

**Args**:

+ broadcaster_id (str): The broadcaster running Predictions  
                        Provided broadcaster_id must match the user_id in the user OAuth token  

+ title (str): Title for the Prediction  
               Maximum: 45 characters

+ outcomes (list): Array of outcome objects with titles for the Prediction  
                   Array size must be 2  
                   The first outcome object is the "blue" outcome and the second outcome object is the "pink" outcome when viewing the Prediction on Twitch

+ prediction_window (int): Total duration for the Prediction (in seconds)  
                           Minimum: 1  
                           Maximum: 1800

**Returns**: dict

### End prediction

~~~
function end_prediction(broadcaster_id,id,status,winning_outcome_id="")
~~~

Lock, resolve, or cancel a Channel Points Prediction  
Active Predictions can be updated to be "locked", "resolved", or "canceled"  
Locked Predictions can be updated to be "resolved" or "canceled"

**Args**:

+ broadcaster_id (str): The broadcaster running prediction events  
                        Provided broadcaster_id must match the user_id in the user OAuth token

+ id (str): ID of the Prediction

+ status (str): The Prediction status to be set  
                Valid values: "RESOLVED", "CANCELED", "LOCKED"

+ winning_outcome_id (str, optional): ID of the winning outcome for the Prediction  
                                      This parameter is required if status is being set to RESOLVED

**Returns**: dict

### Get channel stream schedule

~~~
function get_channel_stream_schedule(broadcaster_id,id=[],start_time="",utc_offset="0",first=20)
~~~

Gets all scheduled broadcasts or specific scheduled broadcasts from a channel’s stream schedule  
Scheduled broadcasts are defined as "stream segments"

**Args**:

+ broadcaster_id (str): User ID of the broadcaster who owns the channel streaming schedule  
                        Provided broadcaster_id must match the user_id in the user OAuth token

+ id (str, optional): The ID of the stream segment to return  
                      Maximum: 100

+ start_time (str, optional): A timestamp in RFC3339 format to start returning stream segments from  
                              If not specified, the current date and time is used

+ utc_offset (str, optional): A timezone offset for the requester specified in minutes  
                              If not specified, "0" is used for GMT

+ first (int, optional): Maximum number of stream segments to return  
                         Default: 20

**Returns**: list

### Get channel iCalendar

~~~
function get_channel_iCalendar(broadcaster_id)
~~~

Gets all scheduled broadcasts from a channel’s stream schedule as an iCalendar

**Args**:

+ broadcaster_id (str): User ID of the broadcaster who owns the channel streaming schedule

**Returns**: str

### Update channel stream schedule

~~~
function update_channel_stream_schedule(broadcaster_id,is_vacation_enabled=False,vacation_start_time="",vacation_end_time="",timezone="")
~~~

Update the settings for a channel’s stream schedule  
This can be used for setting vacation details

**Args**:

+ broadcaster_id (str): User ID of the broadcaster who owns the channel streaming schedule  
                        Provided broadcaster_id must match the user_id in the user OAuth token

+ is_vacation_enabled (bool, optional): Indicates if Vacation Mode is enabled  
                                        Set to true to add a vacation or false to remove vacation from the channel streaming schedule

+ vacation_start_time (str, optional): Start time for vacation specified in RFC3339 format  
                                       Required if is_vacation_enabled is set to true

+ vacation_end_time (str, optional): End time for vacation specified in RFC3339 format  
                                     Required if is_vacation_enabled is set to true

+ timezone (str, optional): The timezone for when the vacation is being scheduled using the IANA time zone database format  
                            Required if is_vacation_enabled is set to true

**Returns**: dict

### Create channel stream schedule segment

~~~
function create_channel_stream_schedule_segment(broadcaster_id,start_time,timezone,is_recurring,duration=240,category_id="",title="")
~~~

Create a single scheduled broadcast or a recurring scheduled broadcast for a channel’s stream schedule

**Args**:

+ broadcaster_id (str): User ID of the broadcaster who owns the channel streaming schedule  
                        Provided broadcaster_id must match the user_id in the user OAuth token

+ start_time (str): Start time for the scheduled broadcast specified in RFC3339 format

+ timezone (str): The timezone of the application creating the scheduled broadcast using the IANA time zone database format

+ is_recurring (bool): Indicates if the scheduled broadcast is recurring weekly

+ duration (int, optional): Duration of the scheduled broadcast in minutes from the start_time  
                            Default: 240

+ category_id (str, optional): Game/Category ID for the scheduled broadcast

+ title (str, optional): Title for the scheduled broadcast  
                         Maximum: 140 characters

**Returns**: dict

### Update channel stream schedule segment

~~~
function update_channel_stream_schedule_segment(broadcaster_id,id,start_time="",duration=240,category_id="",title="",is_canceled=False,timezone="")
~~~

Update a single scheduled broadcast or a recurring scheduled broadcast for a channel’s stream schedule

**Args**:

+ broadcaster_id (str): User ID of the broadcaster who owns the channel streaming schedule  
                        Provided broadcaster_id must match the user_id in the user OAuth token

+ id (str): The ID of the streaming segment to update

+ start_time (str, optional): Start time for the scheduled broadcast specified in RFC3339 format

+ duration (int, optional): Duration of the scheduled broadcast in minutes from the start_time  
                            Default: 240

+ category_id (str, optional): Game/Category ID for the scheduled broadcast

+ title (str, optional): Title for the scheduled broadcast  
                         Maximum: 140 characters

+ is_canceled (bool, optional): Indicated if the scheduled broadcast is canceled

+ timezone (str, optional): The timezone of the application creating the scheduled broadcast using the IANA time zone database format

**Returns**: dict

### Delete channel stream schedule segment

~~~
function delete_channel_stream_schedule_segment(broadcaster_id,id)
~~~

Delete a single scheduled broadcast or a recurring scheduled broadcast for a channel’s stream schedule

**Args**:

+ broadcaster_id (str): User ID of the broadcaster who owns the channel streaming schedule  
                        Provided broadcaster_id must match the user_id in the user OAuth token

+ id (str): The ID of the streaming segment to delete

### Search categories

~~~
function search_categories(query,first=20)
~~~

Returns a list of games or categories that match the query via name either entirely or partially

**Args**:

+ query (str): URI encoded search query

+ first (int, optional): Maximum number of objects to return
                         Default: 20

**Returns**: list

### Search channels

~~~
function search_channels(query,first=20,live_only=False)
~~~

Returns a list of channels (users who have streamed within the past 6 months) that match the query via channel name or description either entirely or partially

**Args**:

+ query (str): URI encoded search query

+ first (int, optional): Maximum number of objects to return  
                         Default: 20

+ live_only (bool, optional): Filter results for live streams only  
                              Default: false

**Returns**: list

### Get stream key

~~~
function get_stream_key(broadcaster_id)
~~~

Gets the channel stream key for a user

**Args**:

+ broadcaster_id (str): User ID of the broadcaster

**Returns**: str

### Get streams

~~~
function get_streams(first=20,game_id="",language="",user_id="",user_login="")
~~~

Gets active streams

**Args**:

+ first (int, optional): Maximum number of objects to return  
                         Default: 20

+ game_id (str, optional): Returns streams broadcasting a specified game ID

+ language (str, optional): Stream language  
                            A language value must be either the ISO 639-1 two-letter code for a supported stream language or "other"

+ user_id (str, optional): Returns streams broadcast by a specified user ID

+ user_login (str, optional): Returns streams broadcast by a specified user login name

**Returns**: list

### Get followed streams

~~~
function get_followed_streams(user_id,first=100)
~~~

Gets information about active streams belonging to channels that the authenticated user follows

**Args**:

+ user_id (str): Results will only include active streams from the channels that this Twitch user follows  
                 user_id must match the User ID in the bearer token

+ first (int, optional): Maximum number of objects to return  
                         Default: 100

**Returns**: list

### Create stream marker

~~~
function create_stream_marker(user_id,description="")
~~~

Creates a marker in the stream of a user specified by user ID  
A marker is an arbitrary point in a stream that the broadcaster wants to mark; e.g., to easily return to later  
The marker is created at the current timestamp in the live broadcast when the request is processed

**Args**:

+ user_id (str): ID of the broadcaster in whose live stream the marker is created

+ description (str, optional): Description of or comments on the marker  
                               Max length is 140 characters

**Returns**: list

### Get stream markers

~~~
function get_stream_markers(user_id="",video_id="",first=20)
~~~

Gets a list of markers for either a specified user’s most recent stream or a specified VOD/video (stream)  
A marker is an arbitrary point in a stream that the broadcaster wants to mark; e.g., to easily return to later  
The only markers returned are those created by the user identified by the Bearer token  
Only one of user_id and video_id must be specified

**Args**:

+ user_id (str, optional): ID of the broadcaster from whose stream markers are returned

+ video_id (str, optional): ID of the VOD/video whose stream markers are returned

+ first (int, optional): Number of values to be returned when getting videos by user or game ID  
                         Default: 20

**Returns**: list

### Get broadcaster subscriptions

~~~
function get_broadcaster_subscriptions(broadcaster_id,user_id=[],first=20)
~~~

Get all of a broadcaster’s subscriptions

**Args**:

+ broadcaster_id (str): User ID of the broadcaster  
                        Must match the User ID in the Bearer token

+ user_id (list, optional): Filters results to only include potential subscriptions made by the provided user ID  
                            Accepts up to 100 values

+ first (int, optional): Maximum number of objects to return  
                         Default: 20

**Returns**: list

### Check user subscription

~~~
function check_user_subscription(broadcaster_id,user_id)
~~~

Checks if a specific user (user_id) is subscribed to a specific channel (broadcaster_id)

**Args**:

+ broadcaster_id (str): User ID of an Affiliate or Partner broadcaster

+ user_id (str): User ID of a Twitch viewer

**Returns**: dict

### Get all stream tags

~~~
function get_all_stream_tags(first=20,tag_id=[])
~~~

Gets the list of all stream tags defined by Twitch

**Args**:

+ first (int, optional): Maximum number of objects to return
                         Default: 20

+ tag_id (list, optional): ID of a tag

**Returns**: list

### Get stream tags

~~~
function get_stream_tags(broadcaster_id)
~~~

Gets the list of current stream tags that have been set for a channel

**Args**:

+ broadcaster_id (str): User ID of the channel to get tags

**Returns**: list

### Replace stream tags

~~~
function replace_stream_tags(broadcaster_id,tag_ids=[])
~~~

Applies specified tags to a specified stream (channel), overwriting any existing tags applied to that stream  
If no tags are specified, all tags previously applied to the stream are removed  
Automated tags are not affected by this operation

**Args**:

+ broadcaster_id (str): ID of the stream for which tags are to be replaced

+ tag_ids (list, optional): IDs of tags to be applied to the stream

### Get channel teams

~~~
function get_channel_teams(broadcaster_id)
~~~

Retrieves a list of Twitch Teams of which the specified channel/broadcaster is a member

**Args**:

+ broadcaster_id (str): User ID for a Twitch user

**Returns**: list

### Get teams

~~~
function get_teams(name="",id="")
~~~

Gets information for a specific Twitch Team  
One of the two optional query parameters must be specified to return Team information

**Args**:

+ name (str, optional): Team name

+ id (str, optional): Team ID

**Returns**: Team

### Get users

~~~
function get_users(id=[],login=[])
~~~

Gets an user  
Users are identified by optional user IDs and/or login name  
If neither a user ID nor a login name is specified, the user is looked up by Bearer token

**Args**:

+ id (list, optional): User ID  
                       Limit: 100

+ login (list, optional): User login name  
                          Limit: 100

**Returns**: list

### Update user

~~~
function update_user(description="")
~~~

Updates the description of a user specified by the bearer token  
If the description parameter is not provided, no update will occur and the current user data is returned

**Args**:

+ description (str, optional): User’s account description

**Returns**: User

### Get user follows

~~~
function get_user_follows(first=20,from_id="",to_id="")
~~~

Gets information on follow relationships between two Twitch users  
At minimum, from_id or to_id must be provided for a query to be valid

**Args**:

+ first (int, optional): Maximum number of objects to return  
                         Default: 20

+ from_id (str, optional): User ID  
                           The request returns information about users who are being followed by the from_id user

+ to_id (str, optional): User ID  
                         The request returns information about users who are following the to_id user

**Returns**: list

### Get user block list

~~~
function get_user_block_list(broadcaster_id,first=20)
~~~

Gets a specified user’s block list

**Args**:

+ broadcaster_id (str): User ID for a Twitch user

+ first (int, optional): Maximum number of objects to return  
                         Default: 20

**Returns**: list

### Block user

~~~
function block_user(target_user_id,source_context="",reason="")
~~~

Blocks the specified user on behalf of the authenticated user

**Args**:

+ target_user_id (str): User ID of the user to be blocked

+ source_context (str, optional): Source context for blocking the user  
                                  Valid values: "chat", "whisper"

+ reason (str, optional): Reason for blocking the user  
                          Valid values: "spam", "harassment", or "other"

### Unblock user

~~~
function unblock_user(target_user_id)
~~~

Unblocks the specified user on behalf of the authenticated user

**Args**:

+ target_user_id (str): User ID of the user to be unblocked

### Get user extensions

~~~
function get_user_extensions()
~~~

Gets a list of all extensions (both active and inactive) for a specified user, identified by a Bearer token

**Returns**: list

### Get user active extensions

~~~
function get_user_active_extensions(user_id="")
~~~

Gets information about active extensions installed by a specified user, identified by a user ID or Bearer token

**Args**:

+ user_id (str, optional): ID of the user whose installed extensions will be returned

**Returns**: list

### Update user extensions

~~~
function update_user_extensions()
~~~

Updates the activation state, extension ID, and/or version number of installed extensions for a specified user, identified by a Bearer token  
If you try to activate a given extension under multiple extension types, the last write wins (and there is no guarantee of write order)

**Returns**: list

### Get videos

~~~
function get_videos(id=[],user_id="",game_id="",first=20,language="",period="all",sort="time",type="all")
~~~

Gets video information by video ID, user ID, or game ID  
Each request must specify one video id, one user_id, or one game_id

**Args**:

+ id (list): ID of the video being queried  
             Limit: 100  
             If this is specified, you cannot use first, language, period, sort and type

+ user_id (str): ID of the user who owns the video

+ game_id (str): ID of the game the video is of

+ first (int, optional): Number of values to be returned when getting videos by user or game ID  
                         Default: 20

+ language (str, optional): Language of the video being queried  
                            A language value must be either the ISO 639-1 two-letter code for a supported stream language or "other"

+ period (str, optional): Period during which the video was created  
                          Valid values: "all", "day", "week", "month"

+ sort (str, optional): Sort order of the videos  
                        Valid values: "time", "trending", "views"  
                        Default: "time"

+ type (str, optional): Type of video  
                        Valid values: "all", "upload", "archive", "highlight"  
                        Default: "all"

**Returns**: list

### Delete video

~~~
function delete_video(id)
~~~

Deletes a video  
Videos are past broadcasts, Highlights, or uploads

**Args**:

+ id (str): ID of the video(s) to be deleted
            Limit: 5

### Get webhook subscriptions

~~~
function get_webhook_subscriptions(first=20)
~~~

Gets the Webhook subscriptions of an application identified by a Bearer token, in order of expiration

**Args**:

+ first (int, optional): Number of values to be returned  
                         Default: 20

**Returns**: list

### Get chatters

~~~
function get_chatters(username)
~~~

Gets all users in a chat

**Args**:

+ channel_name (str): Name of the user who is owner of the chat

**Returns**: dict

### Send

~~~
function send(channel,text)
~~~

Sends a message by chat

**Args**:

+ channel (str): Owner of the chat

+ text (str): Message's text

### Ban

~~~
function ban(channel,user,reason="")
~~~

Bans a user

**Args**:

+ channel (str): Channel who bans

+ username (str): User to ban

+ reason (str, optional): Reason of the ban

### Unban

~~~
function unban(channel,user)
~~~

Undoes the ban of a user

**Args**:

+ channel (str): Name of the channel who readmits

+ user (str): Name of the user to readmit

### Clear

~~~
function clear(channel)
~~~

Clears the chat

**Args**:

+ channel (str): Channel to clean the chat

### Delete poll

~~~
function delete_poll(channel)
~~~

Eliminates the active poll

**Args**:

+ channel (str): Channel in which eliminate the poll

### Emoteonly

~~~
function emoteonly(channel)
~~~

Activates the "emotes only" mode

**Args**:

+ channel (str): Channel on which activate the mode

### Emoteonly off

~~~
function emoteonly_off(channel)
~~~

Disables "emotes only" mode

**Args**:

+ channel (str): Channel on which disable the mode

### End poll

~~~
function endpoll(channel)
~~~

Finish the active poll

**Args**:

+ channel (str): Channel in which finish the poll

### Followers

~~~
function followers(channel)
~~~

Activates the "followers only" mode

**Args**:

+ channel (str): Channel on which activate the mode

### Followers off

~~~
function followers_off(channel)
~~~

Disables the "followers only" mode

**Args**:

+ channel (str): Channel on which disable the mode

### Host

~~~
function host(channel,username)
~~~

Hosts a channel

**Args**:

+ channel (str): Name of the channel who hosts

+ username (str): Name of the channel to host

### Unhost

~~~
function unhost(channel)
~~~

Unhosts the hosted channel

**Args**:

+ channel (str): Channel who unhosts

### Marker

~~~
function marker(channel,description="")
~~~

Leaves a mark on the channel's stream

**Args**:

+ channel (str): Channel in which leave the mark

+ description (str): Mark's description

### Mod

~~~
function mod(channel,username)
~~~

Makes a user mod

**Args**:

+ channel (str): Channel who promotes the user

+ username (str): Name of the user to be promoted

### Unmod

~~~
function unmod(channel,username)
~~~

Removes the moderator's rank from a user

**Args**:

+ channel (str): Channel who removes the moderator's rank

+ username (str): User's name

### Poll

~~~
function poll(channel)
~~~

Opens a configuration menu for creating a poll

**Args**:

+ channel (str): Channel in which create the poll

### Prediction

~~~
function prediction(channel)
~~~

Opens a configuration menu for creating a prediction

**Args**:

+ channel (str): Channel in which create the prediction

### Raid

~~~
function raid(channel,username)
~~~

Raids another channel

**Args**:

+ channel (str): Name of the channel who raids

+ username (str): Name of the channel to raid

### Unraid

~~~
function unraid(channel)
~~~

Cancels an raid

**Args**:

+ channel (str): Channel who unraids

### Requests

~~~
function requests(channel)
~~~

Opens the reward requests queue

**Args**:

+ channel (str): Owner of the rewards

### Slow

~~~
function slow(channel,duration)
~~~

Activates the "slow" mode

**Args**:

+ channel (str): Channel on which activate the mode

+ duration (int): Time between messages

### Slow off

~~~
function slow_off(channel)
~~~

Disables the "slow" mode

**Args**:

+ channel (str): Channel on which disable the mode

### Subscribers

~~~
function subscribers(channel)
~~~

Activates the "subscribers only" mode

**Args**:

+ channel (str): Channel on which activate the mode

### Subscribers off

~~~
function subscribers_off(channel)
~~~

Disables "subscriber only" mode

**Args**:

+ channel (str): Channel on which disable the mode

### Timeout

~~~
function timeout(channel,user,duration=600,reason="")
~~~

Expels a user temporarily

**Args**:

+ channel (str): Channel who ejects

+ user (str): Name of the user to expel

+ duration (int): Ejecting time

+ reason (str): Reason for expulsion

### Untimeout

~~~
function untimeout(channel,username)
~~~

Cancels the timeout of a user

**Args**:

+ channel (str): Channel who ejected the user

+ username (str): User to readmit

### Uniquechat

~~~
function uniquechat(channel)
~~~

Activates the "unique" mode

**Args**:

+ channel (str): Channel on which activate the mode

### Uniquechat off

~~~
function uniquechat_off(channel)
~~~

Disables the "unique" mode

**Args**:

+ channel (str): Channel on which disable the mode

### User

~~~
function user(channel,username)
~~~

Shows information about a user

**Args**:

+ channel (str): Channel in which to show the user's information

+ username (str): User to show information about

### Vip

~~~
function vip(self,channel,username):
~~~

Makes a user vip

**Args**:

+ channel (str): Channel who makes a user vip

+ username (str): User's name

### Unvip

~~~
function unvip(channel,username)
~~~

Removes the vip range from a user

**Args**:

+ channel (str): Channel who remove's the vip range

+ username (str): User's name

### Block

~~~
function block(channel,user)
~~~

Blocks a user

**Args**:

+ channel (str): Channel who blocks

+ username (str): User to block

### Unblock

~~~
function unblock(channel,user)
~~~

Unblocks a user

**Args**:

+ channel (str): Name of the channel who unblocks

+ user (str): Name of the user to unblock

### Color

~~~
function color(channel,color)
~~~

Changes the color of the channel's name in the chat

**Args**:

+ channel (str): Channel to change color

+ color (str): New color's name

### Help

~~~
function help(channel,command)
~~~

Shows detailed information about a command

**Args**:

+ channel (str): Channel in which show the command's information

+ command (str): Command to show information about

### Me

~~~
function me(channel,text)
~~~

Sends a message by chat in italics

**Args**:

+ channel (str): Owner of the chat

+ text (str): Message's text

### Mods

~~~
function mods(channel)
~~~

Shows the moderators list of a channel

**Args**:

+ channel (str): Channel who owns the moderators

### Vips

~~~
function vips(channel)
~~~

Shows the vips list of a channel

**Args**:

+ channel (str): Channel who owns the vips

### Vote

~~~
function vote(channel,index)
~~~

Votes in the active poll

**Args**:

+ channel (str): Owner of the poll

+ index (int): Number of the option

### Commercial

~~~
function commercial(channel,duration=30)
~~~

Places advertising in the channel

**Args**:

+ channel (str): Channel on which start the commercial

+ duration (int): Duration of advertising

### Whisper

~~~
function whisper(channel,user,text)
~~~

Whispers to a user

**Args**:

+ channel (str): Channel on which send the whisp

+ user (str): User's name

+ text (str): Whisper's text

### Add method after commands

~~~
function add_method_after_commands(name,method)
~~~

Adds to the bot a method that will be executed after each command

**Args**:

+ name (str): Method's name

+ method (func): Method to be executed after each command

### Add method before commands

~~~
function add_method_before_commands(name,method)
~~~

Adds to the bot a method that will be executed before each command

**Args**:

+ name (str): Method's name

+ method (func): Method to be executed before each command

### Remove check

~~~
function remove_check(name)
~~~

Removes a check from the bot

**Args**:

+ name (str): Check's name

### Remove listener

~~~
function remove_listener(name)
~~~

Removes a listener from the bot

**Args**:

+ name (str): Listener's name

### Remove command

~~~
function remove_command(name)
~~~

Removes a command from the bot

**Args**:

+ name (str): Command's name

### Remove method after commands

~~~
function remove_method_after_commands(name)
~~~

Removes a method that is executed after each command

**Args**:

+ name (str): Method's name

### Remove method before commands

~~~
function remove_method_before_commands(name)
~~~

Removes a method that is executed before each command

**Args**:

+ name (str): Method's name

## User

~~~
class User(id,login,display_name,type,broadcaster_type,description,profile_image_url,offline_image_url,view_count)
~~~

Represents an user

**Args**:

+ id (int): User's ID

+ login (str): User's login

+ display_name (str): User's name

+ type (str): User type

+ broadcaster_type (str): User's range

+ description (str): User's description

+ profile_image_url (str): URL of the user's profile image

+ offline_image_url (str): URL of the image that is displayed when the user is not on stream

+ view_count (int): Number of user viewers

## Game

~~~
class Game(id,name,box_art_url)
~~~

Represents a Twitch category

**Args**:

+ id (int): Category's ID

+ name (str): Category's name

+ box_art_url (str): URL of the category's image

## Stream

~~~
class Stream(id,user_id,user_name,game_id,type,title,viewer_count,started_at,language,thumbnail_url,tag_ids)
~~~

Represents a stream

**Args**:

+ id (int): Stream's ID

+ user_id (int): Channel's ID

+ user_name (str): Channel's name

+ game_id (int): Stream's category's ID

+ type (str): Stream's status

+ title (str): Stream's title

+ viewer_count (int): Number of viewers

+ started_at (str): Stream's start date and time

+ language (str): Stream's language

+ thumbnail_url (str): URL of the preview image

+ tag_ids (list): IDs of the stream's tags

## Message

~~~
class Message(prefix,user,channel,irc_command,irc_args,text,text_command,text_args)
~~~

Represents a message

**Args**:

+ prefix (str): Message's refix

+ user (str): User who has sent the message

+ channel (str): Channel on which the message was sent

+ irc_command (str): IRC command related to the message

+ irc_args (str): IRC command's arguments

+ text (str): Message's text

+ text_command (str): Command related to the message

+ text_args (str): Command's arguments

## Reward

~~~
class Reward(broadcaster_name,broadcaster_id,id,image,background_color,is_enabled,cost,title,prompt,is_user_input_required,max_per_stream_setting,max_per_user_per_stream_setting,global_cooldown_setting,is_paused,is_in_stock,default_image,should_redemptions_skip_request_queue,redemptions_redeemed_current_stream,cooldown_expires_at)
~~~

Represents a reward

**Args**:

+ broadcaster_name (str): Name of the channel owner of the reward

+ broadcaster_id (str): ID of the channel owner of the reward

+ id (str): ID of the reward

+ image (str): Image of the reward

+ background_color (str): Background color of the reward

+ is_enabled (bool): Is the reward currently enabled

+ cost (int): The cost of the reward

+ title (str): The title of the reward

+ prompt (str): The prompt for the viewer when they are redeeming the reward

+ is_user_input_required (bool): Does the user need to enter information when redeeming the reward

+ max_per_stream_setting (dict): Settings about maximum uses per stream

+ max_per_user_per_stream_setting (dict): Settings about maximum uses per stream and user

+ global_cooldown_setting (dict): Settings about global cooldown

+ is_paused (bool): Is the reward currently paused

+ is_in_stock (bool): Is the reward currently in stock

+ default_image (dict): Default images of the reward

+ should_redemptions_skip_request_queue (bool): Should redemptions be set to FULFILLED status immediately when redeemed and skip the request queue instead of the normal UNFULFILLED status

+ redemptions_redeemed_current_stream (int): The number of redemptions redeemed during the current live stream

+ cooldown_expires_at (int): Timestamp of the cooldown expiration

## Redemption

~~~
class Redemption(broadcaster_name,broadcaster_id,id,user_id,user_name,user_input,status,redeemed_at,reward)
~~~

Represents a reward redemption

**Args**:

+ broadcaster_name (str): The display name of the broadcaster that the reward belongs to

+ broadcaster_id (str): The id of the broadcaster that the reward belongs to

+ id (str): The ID of the redemption

+ user_id (str): The ID of the user that redeemed the reward

+ user_name (str): The display name of the user that redeemed the reward

+ user_input (str): The user input provided

+ status (str): One of UNFULFILLED, FULFILLED or CANCELED

+ redeemed_at (str): Timestamp of when the reward was redeemed

+ reward (Reward): The custom reward that was redeemed at the time it was redeemed

## Video

~~~
class Video(id,user_id,user_name,title,description,created_at,published_at,url,thumbnail_url,viewable,view_count,language,type,duration)
~~~

Represents a video

**Args**:

+ id (str): ID of the video

+ user_id (str): ID of the owner of the video

+ user_name (str): User name of the owner of the video

+ title (str): Title of the video

+ description (str): Description of the video

+ created_at (str): Date of creation of the video

+ published_at (str): Date of publication of the video

+ url (str): URL of the video

+ thumbnail_url (str): URL of the preview image of the video

+ viewable (str): Indicates whether the video is publicly viewable

+ view_count (int): Number of times the video has been viewed

+ language (str): Language of the video

+ type (str): Type of the video

+ duration (str): Duration of the video

## Team

~~~
class Team(users,background_image_url,banner,created_at,updated_at,info,thumbnail_url,team_name,team_display_name,id)
~~~

Represents a team

**Args**:

+ users (list): Users in the team

+ background_image_url (str): URL of the team background image

+ banner (str): URL for the team banner

+ created_at (str): Date and time the team was created

+ updated_at (str): Date and time the team was last updated

+ info (str): Team description

+ thumbnail_url (str): Image URL for the team logo

+ team_name (str): Team name

+ team_display_name (str): Team display name

+ id (str): Team ID