import socket
import ssl
from typing import Callable

from .client import Client
from .dataclasses import Message

_IRC_SERVER = "irc.chat.twitch.tv"
_IRC_PORT = 6697

_DEFAULT_TIMEOUT = 10


class Bot:
    """
    Represents a bot
    """

    def __init__(
        self,
        oauth_token: str,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        tokens_path: str,
        username: str,
        channels: list[str],
        command_prefix: str,
        authorization_code: str | None = None,
        jwt_token: str | None = None,
        ready_message: str | None = None,
    ):
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
            code (str): Authorization code for getting an user token
            jwt_token (str): JWT Token
            ready_message (str): Message that the bot will send through the chats of the channels it access
        """

        self.client = Client(
            client_id,
            client_secret,
            redirect_uri,
            tokens_path,
            authorization_code,
            jwt_token,
        )
        self.__oauth_token = oauth_token
        self.__finish = False
        self.username = username

        self.channels = []

        for channel in channels:
            self.channels.append(channel.replace("@", "").lower())

        self.command_prefix = command_prefix
        self.ready_message = ready_message if ready_message is not None else ""

        self.custom_methods_before_join_channel = {}
        self.methods_before_join_channel_to_remove = []
        self.custom_methods_after_join_channel = {}
        self.methods_after_join_channel_to_remove = []

        self.custom_methods_before_leave_channel = {}
        self.methods_before_leave_channel_to_remove = []
        self.custom_methods_after_leave_channel = {}
        self.methods_after_leave_channel_to_remove = []

        self.custom_checks = {}
        self.checks_to_remove = []
        self.custom_listeners = {}
        self.listeners_to_remove = []
        self.custom_commands = {}
        self.commands_to_remove = []
        self.custom_methods_before_commands = {}
        self.methods_before_commands_to_remove = []
        self.custom_methods_after_commands = {}
        self.methods_after_commands_to_remove = []

        self.custom_methods_after_clearchat = {}
        self.methods_after_clearchat_to_remove = []

        self.custom_methods_after_delete_message = {}
        self.methods_after_delete_message_to_remove = []

        self.custom_methods_after_bot_connected = {}
        self.methods_after_bot_connected_to_remove = []

        self.irc = ssl.SSLContext().wrap_socket(socket.socket())

    def __send_command(self, command: str, args: str) -> None:
        print(f"{command} < {args}")

        self.irc.send((command + "\r\n").encode())

    def __send_join(self, channel: str) -> None:
        self.__send_command("JOIN", f"#{channel}")

    def __send_nick(self, username: str) -> None:
        self.__send_command("NICK", username)

    def __send_part(self, channel: str) -> None:
        self.__send_command("PART", f"#{channel}")

    def __send_pass(self, oauth_token: str) -> None:
        self.__send_command("PASS", oauth_token)

    def __send_pong(self, text: str) -> None:
        self.__send_command("PONG", f":{text}")

    def __send_privmsg(self, channel: str, text: str) -> None:
        self.__send_command("PRIVMSG", f"#{channel} :{text}")

    def __login(self) -> None:
        self.__send_pass(self.__oauth_token)
        self.__send_nick(self.username)

    def join_channel(self, channel: str) -> None:
        """
        Makes the bot to join into a channel

        Args:
            channel (str): The channel to join
        """

        self.__execute_methods_before_join_channel(channel)

        self.__send_join(channel)
        self.__send_privmsg(channel, self.ready_message)

        self.__execute_methods_after_join_channel(channel)

        self.__remove_methods_before_join_channel()
        self.__remove_methods_after_join_channel()

    def leave_channel(self, channel: str) -> None:
        """
        Makes the bot to leave into a channel

        Args:
            channel (str): The channel to leave
        """

        self.__execute_methods_before_leave_channel(channel)

        self.__send_part(channel)

        self.__execute_methods_after_leave_channel(channel)

        self.__remove_methods_before_leave_channel()
        self.__remove_methods_after_leave_channel()

    def __connect(self) -> None:
        self.irc.settimeout(_DEFAULT_TIMEOUT)
        self.irc.connect((_IRC_SERVER, _IRC_PORT))

        self.__login()

        for channel in self.channels:
            self.join_channel(channel)

    def run(self) -> None:
        """
        Runs the bot
        """

        self.__connect()
        self.__loop()

    def stop(self) -> None:
        """
        Stops the bot
        """

        self.__finish = True

    def __get_user_from_prefix(self, prefix: str) -> str | None:
        domain = prefix.split("!")[0]

        if domain.endswith(".tmi.twitch.tv"):
            return domain.replace(".tmi.twitch.tv", "")

        if "tmi.twitch.tv" not in domain:
            return domain

        return None

    def __remove_prefix(self, string: str, prefix: str) -> str:
        if not string.startswith(prefix):
            return string

        return string[len(prefix) :]

    def __parse_message(self, received_msg: str) -> Message:
        parts = received_msg.split(" ")

        prefix = None
        user = None
        channel = None
        irc_command = None
        irc_args = None
        text = None
        text_command = None
        text_args = None

        if parts[0].startswith(":"):
            prefix = self.__remove_prefix(parts[0], ":")
            user = self.__get_user_from_prefix(prefix)
            parts = parts[1:]

        text_start = next(
            (idx for idx, part in enumerate(parts) if part.startswith(":")), None
        )

        if text_start is not None:
            text_parts = parts[text_start:]
            text_parts[0] = text_parts[0][1:]
            text = " ".join(text_parts)

            if text_parts[0].startswith(self.command_prefix):
                text_command = self.__remove_prefix(text_parts[0], self.command_prefix)
                text_args = text_parts[1:]

            parts = parts[:text_start]

        irc_command = parts[0]
        irc_args = parts[1:]

        hash_start = next(
            (idx for idx, part in enumerate(irc_args) if part.startswith("#")), None
        )

        if hash_start is not None:
            channel = irc_args[hash_start][1:]

        message = Message(
            prefix,
            user,
            channel,
            irc_command,
            irc_args,
            text,
            text_command,
            text_args,
        )

        return message

    def __execute_methods_before_join_channel(self, channel: str) -> None:
        for method in self.custom_methods_before_join_channel.values():
            method(channel)

    def __remove_methods_before_join_channel(self) -> None:
        for method in self.methods_before_join_channel_to_remove:
            if method in self.custom_methods_before_join_channel:
                self.custom_methods_before_join_channel.pop(method)

        self.methods_before_join_channel_to_remove = []

    def __execute_methods_after_join_channel(self, channel: str) -> None:
        for method in self.custom_methods_after_join_channel.values():
            method(channel)

    def __remove_methods_after_join_channel(self) -> None:
        for method in self.methods_after_join_channel_to_remove:
            if method in self.custom_methods_after_join_channel:
                self.custom_methods_after_join_channel.pop(method)

        self.methods_after_join_channel_to_remove = []

    def __execute_methods_before_leave_channel(self, channel: str) -> None:
        for method in self.custom_methods_before_leave_channel.values():
            method(channel)

    def __remove_methods_before_leave_channel(self) -> None:
        for method in self.methods_before_leave_channel_to_remove:
            if method in self.custom_methods_before_leave_channel:
                self.custom_methods_before_leave_channel.pop(method)

        self.methods_before_leave_channel_to_remove = []

    def __execute_methods_after_leave_channel(self, channel: str) -> None:
        for method in self.custom_methods_after_leave_channel.values():
            method(channel)

    def __remove_methods_after_leave_channel(self) -> None:
        for method in self.methods_after_leave_channel_to_remove:
            if method in self.custom_methods_after_leave_channel:
                self.custom_methods_after_leave_channel.pop(method)

        self.methods_after_leave_channel_to_remove = []

    def __execute_checks(self) -> None:
        for check in self.custom_checks.values():
            check()

    def __remove_checks(self) -> None:
        for check in self.checks_to_remove:
            if check in self.custom_checks:
                self.custom_checks.pop(check)

        self.checks_to_remove = []

    def __execute_listeners(self, message: Message) -> None:
        for listener in self.custom_listeners.values():
            listener(message)

    def __remove_listeners(self) -> None:
        for listener in self.listeners_to_remove:
            if listener in self.custom_listeners:
                self.custom_listeners.pop(listener)

        self.listeners_to_remove = []

    def __execute_command(self, message: Message) -> None:
        self.custom_commands[message.text_command](message)

    def __remove_commands(self) -> None:
        for command in self.commands_to_remove:
            if command in self.custom_commands:
                self.custom_commands.pop(command)

        self.commands_to_remove = []

    def __execute_methods_before_commands(self, message: Message) -> None:
        for before in self.custom_methods_before_commands.values():
            before(message)

    def __remove_methods_before_commands(self) -> None:
        for method in self.methods_before_commands_to_remove:
            if method in self.custom_methods_before_commands:
                self.custom_methods_before_commands.pop(method)

        self.methods_before_commands_to_remove = []

    def __execute_methods_after_commands(self, message: Message) -> None:
        for after in self.custom_methods_after_commands.values():
            after(message)

    def __remove_methods_after_commands(self) -> None:
        for method in self.methods_after_commands_to_remove:
            if method in self.custom_methods_after_commands:
                self.custom_methods_after_commands.pop(method)

        self.methods_after_commands_to_remove = []

    def __execute_methods_after_clearchat(self, channel: str, user: str) -> None:
        for method in self.custom_methods_after_clearchat.values():
            method(channel, user)

    def __remove_methods_after_clearchat(self) -> None:
        for method in self.methods_after_clearchat_to_remove:
            if method in self.custom_methods_after_clearchat:
                self.custom_methods_after_clearchat.pop(method)

        self.methods_after_clearchat_to_remove = []

    def __execute_methods_after_delete_message(self, channel: str, text: str) -> None:
        for method in self.custom_methods_after_delete_message.values():
            method(channel, text)

    def __remove_methods_after_delete_message(self) -> None:
        for method in self.methods_after_delete_message_to_remove:
            if method in self.custom_methods_after_delete_message:
                self.custom_methods_after_delete_message.pop(method)

        self.methods_after_delete_message_to_remove = []

    def __execute_methods_after_bot_connected(self) -> None:
        for method in self.custom_methods_after_bot_connected.values():
            method()

    def __remove_methods_after_bot_connected(self) -> None:
        for method in self.methods_after_bot_connected_to_remove:
            if method in self.custom_methods_after_bot_connected:
                self.custom_methods_after_bot_connected.pop(method)

        self.methods_after_bot_connected_to_remove = []

    def __handle_message(self, received_msg: str) -> None:
        if len(received_msg) == 0:
            return

        message = self.__parse_message(received_msg)

        if message.irc_command == "NOTICE":
            print(f"{message.irc_command} > [{message.channel}]: {message.text}")

        if message.irc_command == "PART":
            print(f"{message.irc_command} > [{message.channel}] {message.user}")

            if message.channel is not None:
                self.__execute_methods_after_leave_channel(message.channel)

            self.__remove_methods_before_leave_channel()
            self.__remove_methods_after_leave_channel()

        if message.irc_command == "PING":
            print(f"{message.irc_command} > :{message.text}")

            if message.text is not None:
                self.__send_pong(message.text)

        if message.irc_command == "PRIVMSG":
            print(
                f"{message.irc_command} > [{message.channel}] {message.user}: {message.text}"
            )

            self.__execute_listeners(message)
            self.__remove_listeners()

            if message.text_command in self.custom_commands:
                self.__execute_methods_before_commands(message)
                self.__remove_methods_before_commands()
                self.__execute_command(message)
                self.__remove_commands()
                self.__execute_methods_after_commands(message)
                self.__remove_methods_after_commands()

        if message.irc_command == "CLEARCHAT":
            print(
                f"{message.irc_command} > [{message.channel}] {message.text if message.text is None else ''}"
            )

            if message.channel is not None and message.text is not None:
                self.__execute_methods_after_clearchat(message.channel, message.text)
                self.__remove_methods_after_clearchat()

        if message.irc_command == "CLEARMSG":
            print(f"{message.irc_command} > [{message.channel}]: {message.text}")

            if message.channel is not None and message.text is not None:
                self.__execute_methods_after_delete_message(
                    message.channel, message.text
                )
                self.__remove_methods_after_delete_message()

        if message.irc_command == "GLOBALUSERSTATE":
            print(f"{message.irc_command} >")

            self.__execute_methods_after_bot_connected()
            self.__remove_methods_after_bot_connected()

    def __loop(self) -> None:
        while not self.__finish:
            try:
                received_msgs = self.irc.recv(2048).decode()

                for received_msg in received_msgs.split("\r\n"):
                    self.__handle_message(received_msg)

            except socket.timeout:
                self.__execute_checks()
                self.__remove_checks()

    def send(self, channel: str, text: str) -> None:
        """
        Sends a message by chat

        Args:
            channel (str): Owner of the chat
            text (str): Message's text
        """

        self.__send_privmsg(channel, text)

    def ban(self, channel: str, user: str, reason: str = "") -> None:
        """
        Bans a user

        Args:
            channel (str): Channel who bans
            username (str): User to ban
            reason (str): Reason of the ban
        """

        self.__send_privmsg(channel, f"/ban @{user} {reason}")

    def unban(self, channel: str, user: str) -> None:
        """
        Undoes the ban of a user

        Args:
            channel (str): Name of the channel who readmits
            user (str): Name of the user to readmit
        """

        self.__send_privmsg(channel, f"/unban @{user}")

    def clear(self, channel: str) -> None:
        """
        Clears the chat

        Args:
            channel (str): Channel to clean the chat
        """

        self.__send_privmsg(channel, "/clear")

    def delete_poll(self, channel: str) -> None:
        """
        Eliminates the active poll

        Args:
            channel (str): Channel in which eliminate the poll
        """

        self.__send_privmsg(channel, "/deletepoll")

    def emoteonly(self, channel: str) -> None:
        """
        Activates the "emotes only" mode

        Args:
            channel (str): Channel on which activate the mode
        """

        self.__send_privmsg(channel, "/emoteonly")

    def emoteonly_off(self, channel: str) -> None:
        """
        Disables "emotes only" mode

        Args:
            channel (str): Channel on which disable the mode
        """

        self.__send_privmsg(channel, "/emoteonlyoff")

    def endpoll(self, channel: str) -> None:
        """
        Finish the active poll

        Args:
            channel (str): Channel in which finish the poll
        """

        self.__send_privmsg(channel, "/endpoll")

    def followers(self, channel: str) -> None:
        """
        Activates the "followers only" mode

        Args:
            channel (str): Channel on which activate the mode
        """

        self.__send_privmsg(channel, "/followers")

    def followers_off(self, channel: str) -> None:
        """
        Disables the "followers only" mode

        Args:
            channel (str): Channel on which disable the mode
        """

        self.__send_privmsg(channel, "/followersoff")

    def host(self, channel: str, username: str) -> None:
        """
        Hosts a channel

        Args:
            channel (str): Name of the channel who hosts
            username (str): Name of the channel to host
        """

        self.__send_privmsg(channel, f"/host {username}")

    def unhost(self, channel: str) -> None:
        """
        Unhosts the hosted channel

        Args:
            channel (str): Channel who unhosts
        """

        self.__send_privmsg(channel, "/unhost")

    def marker(self, channel: str, description: str = "") -> None:
        """
        Leaves a mark on the channel's stream

        Args:
            channel (str): Channel in which leave the mark
            description (str): Mark's description
        """

        self.__send_privmsg(channel, f"/marker {description}")

    def mod(self, channel: str, username: str) -> None:
        """
        Makes a user mod

        Args:
            channel (str): Channel who promotes the user
            username (str): Name of the user to be promoted
        """

        self.__send_privmsg(channel, f"/mod {username}")

    def unmod(self, channel: str, username: str) -> None:
        """
        Removes the moderator's rank from a user

        Args:
            channel (str): Channel who removes the moderator's rank
            username (str): User's name
        """

        self.__send_privmsg(channel, f"/unmod {username}")

    def poll(self, channel: str) -> None:
        """
        Opens a configuration menu for creating a poll

        Args:
            channel (str): Channel in which create the poll
        """

        self.__send_privmsg(channel, "/poll")

    def prediction(self, channel: str) -> None:
        """
        Opens a configuration menu for creating a prediction

        Args:
            channel (str): Channel in which create the prediction
        """

        self.__send_privmsg(channel, "/prediction")

    def raid(self, channel: str, username: str) -> None:
        """
        Raids another channel

        Args:
            channel (str): Name of the channel who raids
            username (str): Name of the channel to raid
        """

        self.__send_privmsg(channel, f"/raid {username}")

    def unraid(self, channel: str) -> None:
        """
        Cancels an raid

        Args:
            channel (str): Channel who unraids
        """

        self.__send_privmsg(channel, "/unraid")

    def requests(self, channel: str) -> None:
        """
        Opens the reward requests queue

        Args:
            channel (str): Owner of the rewards
        """

        self.__send_privmsg(channel, "/requests")

    def slow(self, channel: str, duration: int) -> None:
        """
        Activates the "slow" mode

        Args:
            channel (str): Channel on which activate the mode
            duration (int): Time between messages
        """

        self.__send_privmsg(channel, f"/slow {duration}")

    def slow_off(self, channel: str) -> None:
        """
        Disables the "slow" mode

        Args:
            channel (str): Channel on which disable the mode
        """

        self.__send_privmsg(channel, "/slow_off")

    def subscribers(self, channel: str) -> None:
        """
        Activates the "subscribers only" mode

        Args:
            channel (str): Channel on which activate the mode
        """

        self.__send_privmsg(channel, "/subscribers")

    def subscribers_off(self, channel: str) -> None:
        """
        Disables "subscriber only" mode

        Args:
            channel (str): Channel on which disable the mode
        """

        self.__send_privmsg(channel, "/subscribersoff")

    def timeout(
        self, channel: str, user: str, duration: int = 600, reason: str = ""
    ) -> None:
        """
        Expels a user temporarily

        Args:
            channel (str): Channel who ejects
            user (str): Name of the user to expel
            duration (int): Ejecting time
            reason (str): Reason for expulsion
        """

        self.__send_privmsg(channel, f"/timeout @{user} {duration} {reason}")

    def untimeout(self, channel: str, username: str) -> None:
        """
        Cancels the timeout of a user

        Args:
            channel (str): Channel who ejected the user
            username (str): User to readmit
        """

        self.__send_privmsg(channel, f"/untimeout @{username}")

    def uniquechat(self, channel: str) -> None:
        """
        Activates the "unique" mode

        Args:
            channel (str): Channel on which activate the mode
        """

        self.__send_privmsg(channel, "/uniquechat")

    def uniquechat_off(self, channel: str) -> None:
        """
        Disables the "unique" mode

        Args:
            channel (str): Channel on which disable the mode
        """

        self.__send_privmsg(channel, "/uniquechatoff")

    def user(self, channel: str, username: str) -> None:
        """
        Shows information about a user

        Args:
            channel (str): Channel in which to show the user's information
            username (str): User to show information about
        """

        self.__send_privmsg(channel, f"/user {username}")

    def vip(self, channel: str, username: str) -> None:
        """
        Makes a user vip

        Args:
            channel (str): Channel who makes a user vip
            username (str): User's name
        """

        self.__send_privmsg(channel, f"/vip {username}")

    def unvip(self, channel: str, username: str) -> None:
        """
        Removes the vip range from a user

        Args:
            channel (str): Channel who remove's the vip range
            username (str): User's name
        """

        self.__send_privmsg(channel, f"/unvip {username}")

    def block(self, channel: str, user: str) -> None:
        """
        Blocks a user

        Args:
            channel (str): Channel who blocks
            username (str): User to block
        """

        self.__send_privmsg(channel, f"/block @{user}")

    def unblock(self, channel: str, user: str) -> None:
        """
        Unblocks a user

        Args:
            channel (str): Name of the channel who unblocks
            user (str): Name of the user to unblock
        """

        self.__send_privmsg(channel, f"/unblock @{user}")

    def color(self, channel: str, color: str) -> None:
        """
        Changes the color of the channel's name in the chat

        Args:
            channel (str): Channel to change color
            color (str): New color's name
        """

        self.__send_privmsg(channel, f"/color {color}")

    def help(self, channel: str, command: str) -> None:
        """
        Shows detailed information about a command

        Args:
            channel (str): Channel in which show the command's information
            command (str): Command to show information about
        """

        self.__send_privmsg(channel, f"/help {command}")

    def me(self, channel: str, text: str) -> None:
        """
        Sends a message by chat in italics

        Args:
            channel (str): Owner of the chat
            text (str): Message's text
        """

        self.__send_privmsg(channel, f"/me {text}")

    def mods(self, channel: str) -> None:
        """
        Shows the moderators list of a channel

        Args:
            channel (str): Channel who owns the moderators
        """

        self.__send_privmsg(channel, "/mods")

    def vips(self, channel: str) -> None:
        """
        Shows the vips list of a channel

        Args:
            channel (str): Channel who owns the vips
        """

        self.__send_privmsg(channel, "/vips")

    def vote(self, channel: str, index: int) -> None:
        """
        Votes in the active poll

        Args:
            channel (str): Owner of the poll
            index (int): Number of the option
        """

        self.__send_privmsg(channel, f"/vote {index}")

    def commercial(self, channel: str, duration: int = 30) -> None:
        """
        Places advertising in the channel

        Args:
            channel (str): Channel on which start the commercial
            duration (int): Duration of advertising
        """

        self.__send_privmsg(channel, f"/commercial {duration}")

    def whisper(self, channel: str, user: str, text: str) -> None:
        """
        Whispers to a user

        Args:
            channel (str): Channel on which send the whisp
            user (str): User's name
            text (str): Whisper's text
        """

        self.__send_privmsg(channel, f"/w {user} {text}")

    def add_method_before_join_channel(self, name: str, method: Callable) -> None:
        """
        Adds to the bot a method that will be executed before joinnnig a channel

        Args:
            name (str): Method's name
            method (Callable): Method to be executed before joinnnig a channel
        """

        self.custom_methods_before_join_channel[name] = method

    def remove_method_before_join_channel(self, name: str) -> None:
        """
        Removes a method that is executed before joinning a channel

        Args:
            name (str): Method's name
        """

        self.methods_before_join_channel_to_remove.append(name)

    def add_method_after_join_channel(self, name: str, method: Callable) -> None:
        """
        Adds to the bot a method that will be executed after joinnnig a channel

        Args:
            name (str): Method's name
            method (Callable): Method to be executed after joinnnig a channel
        """

        self.custom_methods_after_join_channel[name] = method

    def remove_method_after_join_channel(self, name: str) -> None:
        """
        Removes a method that is executed after joinning a channel

        Args:
            name (str): Method's name
        """

        self.methods_after_join_channel_to_remove.append(name)

    def add_method_before_leave_channel(self, name: str, method: Callable) -> None:
        """
        Adds to the bot a method that will be executed before leaving a channel

        Args:
            name (str): Method's name
            method (Callable): Method to be executed before leaving a channel
        """

        self.custom_methods_before_leave_channel[name] = method

    def remove_method_before_leave_channel(self, name: str) -> None:
        """
        Removes a method that is executed before leaving a channel

        Args:
            name (str): Method's name
        """

        self.methods_before_leave_channel_to_remove.append(name)

    def add_method_after_leave_channel(self, name: str, method: Callable) -> None:
        """
        Adds to the bot a method that will be executed after leaving a channel

        Args:
            name (str): Method's name
            method (Callable): Method to be executed after leaving a channel
        """

        self.custom_methods_after_leave_channel[name] = method

    def remove_method_after_leave_channel(self, name: str) -> None:
        """
        Removes a method that is executed after leaving a channel

        Args:
            name (str): Method's name
        """

        self.methods_after_leave_channel_to_remove.append(name)

    def add_check(self, name: str, check: Callable) -> None:
        """
        Adds a check to the bot
        Checks work permanently

        Args:
            name (str): Check's name
            check (Callable): Method that will act as a check
        """

        self.custom_checks[name] = check

    def remove_check(self, name: str) -> None:
        """
        Removes a check from the bot

        Args:
            name (str): Check's name
        """

        self.checks_to_remove.append(name)

    def add_listener(self, name: str, listener: Callable) -> None:
        """
        Adds a listener to the bot
        Listeners work only when a message is received
        Listeners must receive as a parameter the last message in the chat

        Args:
            name (str): Command's name
            listener (Callable): Method that will be executed when the command is invoked
        """

        self.custom_listeners[name] = listener

    def remove_listener(self, name: str) -> None:
        """
        Removes a listener from the bot

        Args:
            name (str): Listener's name
        """

        self.listeners_to_remove.append(name)

    def add_command(self, name: str, command: Callable) -> None:
        """
        Adds a command to the bot
        Commands must receive as a parameter the messages which call them

        Args:
            name (str): Command's name
            command (Callable): Method that will be executed when the command is invoked
        """

        self.custom_commands[name] = command

    def remove_command(self, name: str) -> None:
        """
        Removes a command from the bot

        Args:
            name (str): Command's name
        """

        self.commands_to_remove.append(name)

    def add_method_before_commands(self, name: str, method: Callable) -> None:
        """
        Adds to the bot a method that will be executed before each command

        Args:
            name (str): Method's name
            method (func): Method to be executed before each command
        """

        self.custom_methods_before_commands[name] = method

    def remove_method_before_commands(self, name: str) -> None:
        """
        Removes a method that is executed before each command

        Args:
            name (str): Method's name
        """

        self.methods_before_commands_to_remove.append(name)

    def add_method_after_commands(self, name: str, method: Callable) -> None:
        """
        Adds to the bot a method that will be executed after each command

        Args:
            name (str): Method's name
            method (func): Method to be executed after each command
        """

        self.custom_methods_after_commands[name] = method

    def remove_method_after_commands(self, name: str) -> None:
        """
        Removes a method that is executed after each command

        Args:
            name (str): Method's name
        """

        self.methods_after_commands_to_remove.append(name)

    def add_method_after_clearchat(self, name: str, method: Callable) -> None:
        """
        Adds to the bot a method that will be executed after each chat clearing

        Args:
            name (str): Method's name
            method (Callable): Method to be executed after each chat clearing
        """

        self.custom_methods_after_clearchat[name] = method

    def remove_method_after_clearchat(self, name: str) -> None:
        """
        Removes a method that is executed after each chat clearing

        Args:
            name (str): Method's name
        """

        self.methods_after_clearchat_to_remove.append(name)

    def add_method_after_delete_message(self, name: str, method: Callable) -> None:
        """
        Adds to the bot a method that will be executed after each time a message is deleted

        Args:
            name (str): Method's name
            method (Callable): Method to be executed after each time a message is deleted
        """

        self.custom_methods_after_delete_message[name] = method

    def remove_method_after_delete_message(self, name: str) -> None:
        """
        Removes a method that is executed after each time a message is deleted

        Args:
            name (str): Method's name
        """

        self.methods_after_delete_message_to_remove.append(name)

    def add_method_after_bot_connected(self, name: str, method: Callable) -> None:
        """
        Adds to the bot a method that will be executed after a bot connects to a chat

        Args:
            name (str): Method's name
            method (Callable): Method to be executed after a bot connects to a chat
        """

        self.custom_methods_after_bot_connected[name] = method

    def remove_method_after_bot_connected(self, name: str) -> None:
        """
        Removes a method that is executed after a bot connects to a chat

        Args:
            name (str): Method's name
        """

        self.methods_after_bot_connected_to_remove.append(name)
