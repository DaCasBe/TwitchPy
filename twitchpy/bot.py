import logging
import socket
import ssl
from typing import Callable

from .client import Client
from .dataclasses import Message


logger = logging.getLogger(__name__)


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

        self.custom_methods_after_toggle_host = {}
        self.methods_after_toggle_host_to_remove = []

        self.custom_methods_after_server_reconnect = {}
        self.methods_after_server_reconnect_to_remove = []

        self.custom_methods_after_channel_change = {}
        self.methods_after_channel_change_to_remove = []

        self.custom_methods_after_event = {}
        self.methods_after_event_to_remove = []

        self.custom_methods_after_user_join = {}
        self.methods_after_user_join_to_remove = []

        self.custom_methods_after_whisper = {}
        self.methods_after_whisper_to_remove = []

        self.irc = ssl.SSLContext().wrap_socket(socket.socket())

    def __send_command(self, command: str, args: str, tags: str | None = None) -> None:
        logger.info("%s%s < %s", tags + " " if tags is not None else "", command, args)

        self.irc.send(
            (
                f"{tags + ' ' if tags is not None else ''}{command} {args}" + "\r\n"
            ).encode()
        )

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

    def __send_privmsg(
        self, channel: str, text: str, message_to_reply: str | None = None
    ) -> None:
        self.__send_command(
            "PRIVMSG",
            f"#{channel} :{text}",
            (
                f"@reply-parent-msg-id={message_to_reply}"
                if message_to_reply is not None
                else None
            ),
        )

    def __login(self) -> None:
        self.__send_pass(self.__oauth_token)
        self.__send_nick(self.username)

    def __request_irc_capabilities(self) -> None:
        self.__send_command(
            "CAP REQ", ":twitch.tv/commands twitch.tv/membership twitch.tv/tags"
        )

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
        self.__request_irc_capabilities()

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
        irc_tags = None
        irc_args = None
        text = None
        text_command = None
        text_args = None

        if parts[0].startswith("@"):
            irc_tags = dict(
                item.split("=")
                for item in self.__remove_prefix(parts[0], "@").split(";")
            )
            parts = parts[1:]

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
            irc_tags,
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

    def __execute_methods_after_clearchat(self, message: Message) -> None:
        for method in self.custom_methods_after_clearchat.values():
            method(message)

    def __remove_methods_after_clearchat(self) -> None:
        for method in self.methods_after_clearchat_to_remove:
            if method in self.custom_methods_after_clearchat:
                self.custom_methods_after_clearchat.pop(method)

        self.methods_after_clearchat_to_remove = []

    def __execute_methods_after_delete_message(self, message: Message) -> None:
        for method in self.custom_methods_after_delete_message.values():
            method(message)

    def __remove_methods_after_delete_message(self) -> None:
        for method in self.methods_after_delete_message_to_remove:
            if method in self.custom_methods_after_delete_message:
                self.custom_methods_after_delete_message.pop(method)

        self.methods_after_delete_message_to_remove = []

    def __execute_methods_after_bot_connected(self, message: Message) -> None:
        for method in self.custom_methods_after_bot_connected.values():
            method(message)

    def __remove_methods_after_bot_connected(self) -> None:
        for method in self.methods_after_bot_connected_to_remove:
            if method in self.custom_methods_after_bot_connected:
                self.custom_methods_after_bot_connected.pop(method)

        self.methods_after_bot_connected_to_remove = []

    def __execute_methods_after_toggle_host(self, message: Message) -> None:
        for method in self.custom_methods_after_toggle_host.values():
            method(message)

    def __remove_methods_after_toggle_host(self) -> None:
        for method in self.methods_after_toggle_host_to_remove:
            if method in self.custom_methods_after_toggle_host:
                self.custom_methods_after_toggle_host.pop(method)

        self.methods_after_toggle_host_to_remove = []

    def __execute_methods_after_server_reconnect(self, message: Message) -> None:
        for method in self.custom_methods_after_server_reconnect.values():
            method(message)

    def __remove_methods_after_server_reconnect(self) -> None:
        for method in self.methods_after_server_reconnect_to_remove:
            if method in self.custom_methods_after_server_reconnect:
                self.custom_methods_after_server_reconnect.pop(method)

        self.methods_after_server_reconnect_to_remove = []

    def __execute_methods_after_channel_change(self, message: Message) -> None:
        for method in self.custom_methods_after_channel_change.values():
            method(message)

    def __remove_methods_after_channel_change(self) -> None:
        for method in self.methods_after_channel_change_to_remove:
            if method in self.custom_methods_after_channel_change:
                self.custom_methods_after_channel_change.pop(method)

        self.methods_after_channel_change_to_remove = []

    def __execute_methods_after_event(self, message: Message) -> None:
        for method in self.custom_methods_after_event.values():
            method(message)

    def __remove_methods_after_event(self) -> None:
        for method in self.methods_after_event_to_remove:
            if method in self.custom_methods_after_event:
                self.custom_methods_after_event.pop(method)

        self.methods_after_event_to_remove = []

    def __execute_methods_after_user_join(self, message: Message) -> None:
        for method in self.custom_methods_after_user_join.values():
            method(message)

    def __remove_methods_after_user_join(self) -> None:
        for method in self.methods_after_user_join_to_remove:
            if method in self.custom_methods_after_user_join:
                self.custom_methods_after_user_join.pop(method)

        self.methods_after_user_join_to_remove = []

    def __execute_methods_after_whisper(self, message: Message) -> None:
        for method in self.custom_methods_after_whisper.values():
            method(message)

    def __remove_methods_after_whisper(self) -> None:
        for method in self.methods_after_whisper_to_remove:
            if method in self.custom_methods_after_whisper:
                self.custom_methods_after_whisper.pop(method)

        self.methods_after_whisper_to_remove = []

    def __handle_notice(self, message: Message) -> None:
        logger.info(
            "%s > [%s]: %s | %s",
            message.irc_command,
            message.channel,
            message.text,
            message.irc_tags,
        )

    def __handle_part(self, message: Message) -> None:
        logger.info("%s > [%s] %s", message.irc_command, message.channel, message.user)

        self.__execute_methods_after_leave_channel(
            message.channel if message.channel is not None else ""
        )
        self.__remove_methods_after_leave_channel()

    def __handle_ping(self, message: Message) -> None:
        logger.info("%s > :%s", message.irc_command, message.text)

        self.__send_pong(message.text if message.text is not None else "")

    def __handle_privmsg(self, message: Message) -> None:
        logger.info(
            "%s > [%s] %s: %s | %s",
            message.irc_command,
            message.channel,
            message.user,
            message.text,
            message.irc_tags,
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

    def __handle_clearchat(self, message: Message) -> None:
        logger.info(
            "%s > [%s] %s | %s",
            message.irc_command,
            message.channel,
            message.text if message.text is None else "",
            message.irc_tags,
        )

        self.__execute_methods_after_clearchat(message)
        self.__remove_methods_after_clearchat()

    def __handle_clearmsg(self, message: Message) -> None:
        logger.info(
            "%s > [%s]: %s | %s",
            message.irc_command,
            message.channel,
            message.text,
            message.irc_tags,
        )

        self.__execute_methods_after_delete_message(message)
        self.__remove_methods_after_delete_message()

    def __handle_globaluserstate(self, message: Message) -> None:
        logger.info("%s > | %s", message.irc_command, message.irc_tags)

        self.__execute_methods_after_bot_connected(message)
        self.__remove_methods_after_bot_connected()

    def __handle_hosttarget(self, message: Message) -> None:
        logger.info("%s > [%s]: %s", message.irc_command, message.channel, message.text)

        self.__execute_methods_after_toggle_host(message)
        self.__remove_methods_after_toggle_host()

    def __handle_reconnect(self, message: Message) -> None:
        logger.info("%s >", message.irc_command)

        self.__execute_methods_after_server_reconnect(message)
        self.__remove_methods_after_server_reconnect()

    def __handle_roomstate(self, message: Message) -> None:
        logger.info(
            "%s > [%s] | %s", message.irc_command, message.channel, message.irc_tags
        )

        self.__execute_methods_after_channel_change(message)
        self.__remove_methods_after_channel_change()

    def __handle_usernotice(self, message: Message) -> None:
        logger.info(
            "%s > [%s]: %s | %s",
            message.irc_command,
            message.channel,
            message.text if message.text is not None else "",
            message.irc_tags,
        )

        self.__execute_methods_after_event(message)
        self.__remove_methods_after_event()

    def __handle_userstate(self, message: Message) -> None:
        logger.info(
            "%s > [%s] | %s", message.irc_command, message.channel, message.irc_tags
        )

        self.__execute_methods_after_user_join(message)
        self.__remove_methods_after_user_join()

    def __handle_whisper(self, message: Message) -> None:
        logger.info(
            "%s > %s: %s",
            message.irc_command,
            message.irc_args[0] if message.irc_args is not None else "",
            message.text,
        )

        self.__execute_methods_after_whisper(message)
        self.__remove_methods_after_whisper()

    def __handle_message(self, received_msg: str) -> None:
        if len(received_msg) == 0:
            return

        message = self.__parse_message(received_msg)

        if message.irc_command == "NOTICE":
            self.__handle_notice(message)

        elif message.irc_command == "PART":
            self.__handle_part(message)

        elif message.irc_command == "PING":
            self.__handle_ping(message)

        elif message.irc_command == "PRIVMSG":
            self.__handle_privmsg(message)

        elif message.irc_command == "CLEARCHAT":
            self.__handle_clearchat(message)

        elif message.irc_command == "CLEARMSG":
            self.__handle_clearmsg(message)

        elif message.irc_command == "GLOBALUSERSTATE":
            self.__handle_globaluserstate(message)

        elif message.irc_command == "HOSTTARGET":
            self.__handle_hosttarget(message)

        elif message.irc_command == "RECONNECT":
            self.__handle_reconnect(message)

        elif message.irc_command == "ROOMSTATE":
            self.__handle_roomstate(message)

        elif message.irc_command == "USERNOTICE":
            self.__handle_usernotice(message)

        elif message.irc_command == "USERSTATE":
            self.__handle_userstate(message)

        elif message.irc_command == "WHISPER":
            self.__handle_whisper(message)

        else:
            logger.info(
                "%s > [%s] %s: %s",
                message.irc_command,
                message.channel,
                message.user,
                message.text,
            )

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

    def reply(self, channel: str, message_id: str, text: str) -> None:
        """
        Replies to a message in a chat

        Args:
            channel (str): Owner of the chat
            message_id (str): ID of the message being replied to
            text (str): Message's text
        """

        self.__send_privmsg(channel, text, message_id)

    def ban(self, channel: str, user: str, reason: str = "") -> None:
        """
        Bans a user

        Args:
            channel (str): Channel who bans
            username (str): User to ban
            reason (str): Reason of the ban
        """

        self.send(channel, f"/ban @{user} {reason}")

    def unban(self, channel: str, user: str) -> None:
        """
        Undoes the ban of a user

        Args:
            channel (str): Name of the channel who readmits
            user (str): Name of the user to readmit
        """

        self.send(channel, f"/unban @{user}")

    def clear(self, channel: str) -> None:
        """
        Clears the chat

        Args:
            channel (str): Channel to clean the chat
        """

        self.send(channel, "/clear")

    def color(self, channel: str, color: str) -> None:
        """
        Changes the color of the channel's name in the chat

        Args:
            channel (str): Channel to change color
            color (str): New color's name
        """

        self.send(channel, f"/color {color}")

    def commercial(self, channel: str, duration: int = 30) -> None:
        """
        Places advertising in the channel

        Args:
            channel (str): Channel on which start the commercial
            duration (int): Duration of advertising
        """

        self.send(channel, f"/commercial {duration}")

    def delete(self, channel: str, message_id: str) -> None:
        """
        Deletes the specified message from the chat room

        Args:
            channel (str): Channel where the message was sent
            message_id (str): ID of the message
        """

        self.send(channel, f"/delete {message_id}")

    def disconnect(self, channel: str) -> None:
        """
        Closes the session that the command was received from

        Args:
            channel (str): Channel whose session close to
        """

        self.send(channel, "/disconnect")

    def emoteonly(self, channel: str) -> None:
        """
        Activates the "emotes only" mode

        Args:
            channel (str): Channel on which activate the mode
        """

        self.send(channel, "/emoteonly")

    def emoteonlyoff(self, channel: str) -> None:
        """
        Disables "emotes only" mode

        Args:
            channel (str): Channel on which disable the mode
        """

        self.send(channel, "/emoteonlyoff")

    def followers(self, channel: str) -> None:
        """
        Activates the "followers only" mode

        Args:
            channel (str): Channel on which activate the mode
        """

        self.send(channel, "/followers")

    def followersoff(self, channel: str) -> None:
        """
        Disables the "followers only" mode

        Args:
            channel (str): Channel on which disable the mode
        """

        self.send(channel, "/followersoff")

    def help(self, channel: str, command: str = "") -> None:
        """
        Shows detailed information about a command

        Args:
            channel (str): Channel in which show the command's information
            command (str): Command to show information about
        """

        self.send(channel, f"/help {command}")

    def host(self, channel: str, username: str) -> None:
        """
        Hosts a channel

        Args:
            channel (str): Name of the channel who hosts
            username (str): Name of the channel to host
        """

        self.send(channel, f"/host {username}")

    def unhost(self, channel: str) -> None:
        """
        Unhosts the hosted channel

        Args:
            channel (str): Channel who unhosts
        """

        self.send(channel, "/unhost")

    def marker(self, channel: str, description: str = "") -> None:
        """
        Leaves a mark on the channel's stream

        Args:
            channel (str): Channel in which leave the mark
            description (str): Mark's description
        """

        self.send(channel, f"/marker {description}")

    def me(self, channel: str, text: str) -> None:
        """
        Sends a message by chat in italics

        Args:
            channel (str): Owner of the chat
            text (str): Message's text
        """

        self.send(channel, f"/me {text}")

    def mod(self, channel: str, username: str) -> None:
        """
        Makes a user mod

        Args:
            channel (str): Channel who promotes the user
            username (str): Name of the user to be promoted
        """

        self.send(channel, f"/mod {username}")

    def unmod(self, channel: str, username: str) -> None:
        """
        Removes the moderator's rank from a user

        Args:
            channel (str): Channel who removes the moderator's rank
            username (str): User's name
        """

        self.send(channel, f"/unmod {username}")

    def mods(self, channel: str) -> None:
        """
        Shows the moderators list of a channel

        Args:
            channel (str): Channel who owns the moderators
        """

        self.send(channel, "/mods")

    def raid(self, channel: str, username: str) -> None:
        """
        Raids another channel

        Args:
            channel (str): Name of the channel who raids
            username (str): Name of the channel to raid
        """

        self.send(channel, f"/raid {username}")

    def unraid(self, channel: str) -> None:
        """
        Cancels an raid

        Args:
            channel (str): Channel who unraids
        """

        self.send(channel, "/unraid")

    def slow(self, channel: str, duration: int) -> None:
        """
        Activates the "slow" mode

        Args:
            channel (str): Channel on which activate the mode
            duration (int): Time between messages
        """

        self.send(channel, f"/slow {duration}")

    def slowoff(self, channel: str) -> None:
        """
        Disables the "slow" mode

        Args:
            channel (str): Channel on which disable the mode
        """

        self.send(channel, "/slowoff")

    def subscribers(self, channel: str) -> None:
        """
        Activates the "subscribers only" mode

        Args:
            channel (str): Channel on which activate the mode
        """

        self.send(channel, "/subscribers")

    def subscribersoff(self, channel: str) -> None:
        """
        Disables "subscriber only" mode

        Args:
            channel (str): Channel on which disable the mode
        """

        self.send(channel, "/subscribersoff")

    def timeout(self, channel: str, user: str, duration: int = 600) -> None:
        """
        Expels a user temporarily

        Args:
            channel (str): Channel who ejects
            user (str): Name of the user to expel
            duration (int): Ejecting time
        """

        self.send(channel, f"/timeout @{user} {duration}")

    def untimeout(self, channel: str, username: str) -> None:
        """
        Cancels the timeout of a user

        Args:
            channel (str): Channel who ejected the user
            username (str): User to readmit
        """

        self.send(channel, f"/untimeout @{username}")

    def uniquechat(self, channel: str) -> None:
        """
        Activates the "unique" mode

        Args:
            channel (str): Channel on which activate the mode
        """

        self.send(channel, "/uniquechat")

    def uniquechatoff(self, channel: str) -> None:
        """
        Disables the "unique" mode

        Args:
            channel (str): Channel on which disable the mode
        """

        self.send(channel, "/uniquechatoff")

    def vip(self, channel: str, username: str) -> None:
        """
        Makes a user vip

        Args:
            channel (str): Channel who makes a user vip
            username (str): User's name
        """

        self.send(channel, f"/vip {username}")

    def unvip(self, channel: str, username: str) -> None:
        """
        Removes the vip range from a user

        Args:
            channel (str): Channel who remove's the vip range
            username (str): User's name
        """

        self.send(channel, f"/unvip {username}")

    def vips(self, channel: str) -> None:
        """
        Shows the vips list of a channel

        Args:
            channel (str): Channel who owns the vips
        """

        self.send(channel, "/vips")

    def whisper(self, channel: str, user: str, text: str) -> None:
        """
        Whispers to a user

        Args:
            channel (str): Channel on which send the whisp
            user (str): User's name
            text (str): Whisper's text
        """

        self.send(channel, f"/w {user} {text}")

    def add_method_before_join_channel(
        self, name: str, method: Callable[[str], None]
    ) -> None:
        """
        Adds to the bot a method that will be executed before joinnnig a channel

        Args:
            name (str): Method's name
            method (Callable[[str], None]): Method to be executed before joinnnig a channel
        """

        self.custom_methods_before_join_channel[name] = method

    def remove_method_before_join_channel(self, name: str) -> None:
        """
        Removes a method that is executed before joinning a channel

        Args:
            name (str): Method's name
        """

        self.methods_before_join_channel_to_remove.append(name)

    def add_method_after_join_channel(
        self, name: str, method: Callable[[str], None]
    ) -> None:
        """
        Adds to the bot a method that will be executed after joinnnig a channel

        Args:
            name (str): Method's name
            method (Callable[[str], None]): Method to be executed after joinnnig a channel
        """

        self.custom_methods_after_join_channel[name] = method

    def remove_method_after_join_channel(self, name: str) -> None:
        """
        Removes a method that is executed after joinning a channel

        Args:
            name (str): Method's name
        """

        self.methods_after_join_channel_to_remove.append(name)

    def add_method_before_leave_channel(
        self, name: str, method: Callable[[str], None]
    ) -> None:
        """
        Adds to the bot a method that will be executed before leaving a channel

        Args:
            name (str): Method's name
            method (Callable[[str], None]): Method to be executed before leaving a channel
        """

        self.custom_methods_before_leave_channel[name] = method

    def remove_method_before_leave_channel(self, name: str) -> None:
        """
        Removes a method that is executed before leaving a channel

        Args:
            name (str): Method's name
        """

        self.methods_before_leave_channel_to_remove.append(name)

    def add_method_after_leave_channel(
        self, name: str, method: Callable[[str], None]
    ) -> None:
        """
        Adds to the bot a method that will be executed after leaving a channel

        Args:
            name (str): Method's name
            method (Callable[[str], None]): Method to be executed after leaving a channel
        """

        self.custom_methods_after_leave_channel[name] = method

    def remove_method_after_leave_channel(self, name: str) -> None:
        """
        Removes a method that is executed after leaving a channel

        Args:
            name (str): Method's name
        """

        self.methods_after_leave_channel_to_remove.append(name)

    def add_check(self, name: str, check: Callable[[], None]) -> None:
        """
        Adds a check to the bot
        Checks work permanently

        Args:
            name (str): Check's name
            check (Callable[[], None]): Method that will act as a check
        """

        self.custom_checks[name] = check

    def remove_check(self, name: str) -> None:
        """
        Removes a check from the bot

        Args:
            name (str): Check's name
        """

        self.checks_to_remove.append(name)

    def add_listener(self, name: str, listener: Callable[[Message], None]) -> None:
        """
        Adds a listener to the bot
        Listeners work only when a message is received
        Listeners must receive as a parameter the last message in the chat

        Args:
            name (str): Listener's name
            listener (Callable[[Message], None]): Method that will be executed after every chat message
        """

        self.custom_listeners[name] = listener

    def remove_listener(self, name: str) -> None:
        """
        Removes a listener from the bot

        Args:
            name (str): Listener's name
        """

        self.listeners_to_remove.append(name)

    def add_command(self, name: str, command: Callable[[Message], None]) -> None:
        """
        Adds a command to the bot
        Commands must receive as a parameter the messages which call them

        Args:
            name (str): Command's name
            command (Callable[[Message], None]): Method that will be executed when the command is invoked
        """

        self.custom_commands[name] = command

    def remove_command(self, name: str) -> None:
        """
        Removes a command from the bot

        Args:
            name (str): Command's name
        """

        self.commands_to_remove.append(name)

    def add_method_before_commands(
        self, name: str, method: Callable[[Message], None]
    ) -> None:
        """
        Adds to the bot a method that will be executed before each command

        Args:
            name (str): Method's name
            method (Callable[[Message], None]): Method to be executed before each command
        """

        self.custom_methods_before_commands[name] = method

    def remove_method_before_commands(self, name: str) -> None:
        """
        Removes a method that is executed before each command

        Args:
            name (str): Method's name
        """

        self.methods_before_commands_to_remove.append(name)

    def add_method_after_commands(
        self, name: str, method: Callable[[Message], None]
    ) -> None:
        """
        Adds to the bot a method that will be executed after each command

        Args:
            name (str): Method's name
            method (Callable[[Message], None]): Method to be executed after each command
        """

        self.custom_methods_after_commands[name] = method

    def remove_method_after_commands(self, name: str) -> None:
        """
        Removes a method that is executed after each command

        Args:
            name (str): Method's name
        """

        self.methods_after_commands_to_remove.append(name)

    def add_method_after_clearchat(
        self, name: str, method: Callable[[Message], None]
    ) -> None:
        """
        Adds to the bot a method that will be executed after each chat clearing

        Args:
            name (str): Method's name
            method (Callable[[Message], None]): Method to be executed after each chat clearing
        """

        self.custom_methods_after_clearchat[name] = method

    def remove_method_after_clearchat(self, name: str) -> None:
        """
        Removes a method that is executed after each chat clearing

        Args:
            name (str): Method's name
        """

        self.methods_after_clearchat_to_remove.append(name)

    def add_method_after_delete_message(
        self, name: str, method: Callable[[Message], None]
    ) -> None:
        """
        Adds to the bot a method that will be executed after each time a message is deleted

        Args:
            name (str): Method's name
            method (Callable[[Message], None]): Method to be executed after each time a message is deleted
        """

        self.custom_methods_after_delete_message[name] = method

    def remove_method_after_delete_message(self, name: str) -> None:
        """
        Removes a method that is executed after each time a message is deleted

        Args:
            name (str): Method's name
        """

        self.methods_after_delete_message_to_remove.append(name)

    def add_method_after_bot_connected(
        self, name: str, method: Callable[[Message], None]
    ) -> None:
        """
        Adds to the bot a method that will be executed after a bot connects to a chat

        Args:
            name (str): Method's name
            method (Callable[[Message], None]): Method to be executed after a bot connects to a chat
        """

        self.custom_methods_after_bot_connected[name] = method

    def remove_method_after_bot_connected(self, name: str) -> None:
        """
        Removes a method that is executed after a bot connects to a chat

        Args:
            name (str): Method's name
        """

        self.methods_after_bot_connected_to_remove.append(name)

    def add_method_after_toggle_host(
        self, name: str, method: Callable[[Message], None]
    ) -> None:
        """
        Adds to the bot a method that will be executed after a channel toggles hosting

        Args:
            name (str): Method's name
            method (Callable[[Message], None]): Method to be executed after a channel toggles hosting
        """

        self.custom_methods_after_toggle_host[name] = method

    def remove_method_after_toggle_host(self, name: str) -> None:
        """
        Removes a method that is executed after a channel toggles hosting

        Args:
            name (str): Method's name
        """

        self.methods_after_toggle_host_to_remove.append(name)

    def add_method_after_server_reconnect(
        self, name: str, method: Callable[[Message], None]
    ) -> None:
        """
        Adds to the bot a method that will be executed after a reconnect warning

        Args:
            name (str): Method's name
            method (Callable[[Message], None]): Method to be executed after a reconnect warning
        """

        self.custom_methods_after_server_reconnect[name] = method

    def remove_method_after_server_reconnect(self, name: str) -> None:
        """
        Removes a method that is executed after a reconnect warning

        Args:
            name (str): Method's name
        """

        self.methods_after_server_reconnect_to_remove.append(name)

    def add_method_after_channel_change(
        self, name: str, method: Callable[[Message], None]
    ) -> None:
        """
        Adds to the bot a method that will be executed after a channel's chat settings change

        Args:
            name (str): Method's name
            method (Callable[[Message], None]): Method to be executed after a channel's chat settings change
        """

        self.custom_methods_after_channel_change[name] = method

    def remove_method_after_channel_change(self, name: str) -> None:
        """
        Removes a method that is executed after a channel's chat settings change

        Args:
            name (str): Method's name
        """

        self.methods_after_channel_change_to_remove.append(name)

    def add_method_after_event(
        self, name: str, method: Callable[[Message], None]
    ) -> None:
        """
        Adds to the bot a method that will be executed after an event occurs

        Args:
            name (str): Method's name
            method (Callable[[Message], None]): Method to be executed after an event occurs
        """

        self.custom_methods_after_event[name] = method

    def remove_method_after_event(self, name: str) -> None:
        """
        Removes a method that is executed after an event occurs

        Args:
            name (str): Method's name
        """

        self.methods_after_event_to_remove.append(name)

    def add_method_after_user_join(
        self, name: str, method: Callable[[Message], None]
    ) -> None:
        """
        Adds to the bot a method that will be executed after an user joins into a channel

        Args:
            name (str): Method's name
            method (Callable[[Message], None]): Method to be executed after an user joins into a channel
        """

        self.custom_methods_after_user_join[name] = method

    def remove_method_after_user_join(self, name: str) -> None:
        """
        Removes a method that is executed after an user joins into a channel

        Args:
            name (str): Method's name
        """

        self.methods_after_user_join_to_remove.append(name)

    def add_method_after_whisper(
        self, name: str, method: Callable[[Message], None]
    ) -> None:
        """
        Adds to the bot a method that will be executed after a whisper is received

        Args:
            name (str): Method's name
            method (Callable[[Message], None]): Method to be executed after a whisper is received
        """

        self.custom_methods_after_whisper[name] = method

    def remove_method_after_whisper(self, name: str) -> None:
        """
        Removes a method that is executed after a whisper is received

        Args:
            name (str): Method's name
        """

        self.methods_after_whisper_to_remove.append(name)
