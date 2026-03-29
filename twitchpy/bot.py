import asyncio
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
        access_token: str,
        username: str,
        channels: list[str],
        command_prefix: str,
        jwt_token: str | None = None,
        ready_message: str | None = None,
    ):
        """
        Args:
            oauth_token (str): OAuth token
            client_id (str): Client ID
            client_secret (str): Client secret
            access_token (str): Access token
            username (str): Name of the bot
            channels (list): Names of channels the bot will access
            command_prefix (str): Prefix of the commands the bot will recognize
            jwt_token (str): JWT Token
            ready_message (str): Message that the bot will send through the chats of the channels it access
        """

        self.client = Client(
            client_id,
            client_secret,
            access_token,
            jwt_token,
        )
        self._oauth_token = oauth_token
        self._finish = False
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

    def _send_command(self, command: str, args: str, tags: str | None = None) -> None:
        logger.info("%s%s < %s", tags + " " if tags is not None else "", command, args)

        self.irc.send(
            (
                f"{tags + ' ' if tags is not None else ''}{command} {args}" + "\r\n"
            ).encode()
        )

    def _send_join(self, channel: str) -> None:
        self._send_command("JOIN", f"#{channel}")

    def _send_nick(self, username: str) -> None:
        self._send_command("NICK", username)

    def _send_part(self, channel: str) -> None:
        self._send_command("PART", f"#{channel}")

    def _send_pass(self, oauth_token: str) -> None:
        self._send_command("PASS", oauth_token)

    def _send_pong(self, text: str) -> None:
        self._send_command("PONG", f":{text}")

    def _send_privmsg(
        self, channel: str, text: str, message_to_reply: str | None = None
    ) -> None:
        self._send_command(
            "PRIVMSG",
            f"#{channel} :{text}",
            (
                f"@reply-parent-msg-id={message_to_reply}"
                if message_to_reply is not None
                else None
            ),
        )

    def _login(self) -> None:
        self._send_pass(self._oauth_token)
        self._send_nick(self.username)

    def _request_irc_capabilities(self) -> None:
        self._send_command(
            "CAP REQ", ":twitch.tv/commands twitch.tv/membership twitch.tv/tags"
        )

    async def join_channel(self, channel: str) -> None:
        """
        Makes the bot to join into a channel

        Args:
            channel (str): The channel to join
        """

        await self._execute_methods_before_join_channel(channel)

        self._send_join(channel)
        self._send_privmsg(channel, self.ready_message)

        await self._execute_methods_after_join_channel(channel)

        self._remove_methods_before_join_channel()
        self._remove_methods_after_join_channel()

    async def leave_channel(self, channel: str) -> None:
        """
        Makes the bot to leave into a channel

        Args:
            channel (str): The channel to leave
        """

        await self._execute_methods_before_leave_channel(channel)

        self._send_part(channel)

        await self._execute_methods_after_leave_channel(channel)

        self._remove_methods_before_leave_channel()
        self._remove_methods_after_leave_channel()

    async def _connect(self) -> None:
        self.irc.settimeout(_DEFAULT_TIMEOUT)
        self.irc.connect((_IRC_SERVER, _IRC_PORT))

        self._login()
        self._request_irc_capabilities()

        for channel in self.channels:
            await self.join_channel(channel)

    async def run(self) -> None:
        """
        Runs the bot
        """

        await self._connect()
        await self._loop()

    def stop(self) -> None:
        """
        Stops the bot
        """

        self._finish = True

    def _get_user_from_prefix(self, prefix: str) -> str | None:
        domain = prefix.split("!")[0]

        if domain.endswith(".tmi.twitch.tv"):
            return domain.replace(".tmi.twitch.tv", "")

        if "tmi.twitch.tv" not in domain:
            return domain

        return None

    def _remove_prefix(self, string: str, prefix: str) -> str:
        if not string.startswith(prefix):
            return string

        return string[len(prefix) :]

    def _parse_message(self, received_msg: str) -> Message:
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
                for item in self._remove_prefix(parts[0], "@").split(";")
            )
            parts = parts[1:]

        if parts[0].startswith(":"):
            prefix = self._remove_prefix(parts[0], ":")
            user = self._get_user_from_prefix(prefix)
            parts = parts[1:]

        text_start = next(
            (idx for idx, part in enumerate(parts) if part.startswith(":")), None
        )

        if text_start is not None:
            text_parts = parts[text_start:]
            text_parts[0] = text_parts[0][1:]
            text = " ".join(text_parts)

            if text_parts[0].startswith(self.command_prefix):
                text_command = self._remove_prefix(text_parts[0], self.command_prefix)
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

    async def _execute_methods_before_join_channel(self, channel: str) -> None:
        tasks = [
            method(channel)
            for method in self.custom_methods_before_join_channel.values()
        ]
        await asyncio.gather(*tasks)

    def _remove_methods_before_join_channel(self) -> None:
        for method in self.methods_before_join_channel_to_remove:
            if method in self.custom_methods_before_join_channel:
                self.custom_methods_before_join_channel.pop(method)

        self.methods_before_join_channel_to_remove = []

    async def _execute_methods_after_join_channel(self, channel: str) -> None:
        tasks = [
            method(channel)
            for method in self.custom_methods_after_join_channel.values()
        ]
        await asyncio.gather(*tasks)

    def _remove_methods_after_join_channel(self) -> None:
        for method in self.methods_after_join_channel_to_remove:
            if method in self.custom_methods_after_join_channel:
                self.custom_methods_after_join_channel.pop(method)

        self.methods_after_join_channel_to_remove = []

    async def _execute_methods_before_leave_channel(self, channel: str) -> None:
        tasks = [
            method(channel)
            for method in self.custom_methods_before_leave_channel.values()
        ]
        await asyncio.gather(*tasks)

    def _remove_methods_before_leave_channel(self) -> None:
        for method in self.methods_before_leave_channel_to_remove:
            if method in self.custom_methods_before_leave_channel:
                self.custom_methods_before_leave_channel.pop(method)

        self.methods_before_leave_channel_to_remove = []

    async def _execute_methods_after_leave_channel(self, channel: str) -> None:
        tasks = [
            method(channel)
            for method in self.custom_methods_after_leave_channel.values()
        ]
        await asyncio.gather(*tasks)

    def _remove_methods_after_leave_channel(self) -> None:
        for method in self.methods_after_leave_channel_to_remove:
            if method in self.custom_methods_after_leave_channel:
                self.custom_methods_after_leave_channel.pop(method)

        self.methods_after_leave_channel_to_remove = []

    async def _execute_checks(self) -> None:
        tasks = [check() for check in self.custom_checks.values()]
        await asyncio.gather(*tasks)

    def _remove_checks(self) -> None:
        for check in self.checks_to_remove:
            if check in self.custom_checks:
                self.custom_checks.pop(check)

        self.checks_to_remove = []

    async def _execute_listeners(self, message: Message) -> None:
        tasks = [listener(message) for listener in self.custom_listeners.values()]
        await asyncio.gather(*tasks)

    def _remove_listeners(self) -> None:
        for listener in self.listeners_to_remove:
            if listener in self.custom_listeners:
                self.custom_listeners.pop(listener)

        self.listeners_to_remove = []

    async def _execute_command(self, message: Message) -> None:
        await self.custom_commands[message.text_command](message)

    def _remove_commands(self) -> None:
        for command in self.commands_to_remove:
            if command in self.custom_commands:
                self.custom_commands.pop(command)

        self.commands_to_remove = []

    async def _execute_methods_before_commands(self, message: Message) -> None:
        tasks = [
            before(message) for before in self.custom_methods_before_commands.values()
        ]
        await asyncio.gather(*tasks)

    def _remove_methods_before_commands(self) -> None:
        for method in self.methods_before_commands_to_remove:
            if method in self.custom_methods_before_commands:
                self.custom_methods_before_commands.pop(method)

        self.methods_before_commands_to_remove = []

    async def _execute_methods_after_commands(self, message: Message) -> None:
        tasks = [
            after(message) for after in self.custom_methods_after_commands.values()
        ]
        await asyncio.gather(*tasks)

    def _remove_methods_after_commands(self) -> None:
        for method in self.methods_after_commands_to_remove:
            if method in self.custom_methods_after_commands:
                self.custom_methods_after_commands.pop(method)

        self.methods_after_commands_to_remove = []

    async def _execute_methods_after_clearchat(self, message: Message) -> None:
        tasks = [
            method(message) for method in self.custom_methods_after_clearchat.values()
        ]
        await asyncio.gather(*tasks)

    def _remove_methods_after_clearchat(self) -> None:
        for method in self.methods_after_clearchat_to_remove:
            if method in self.custom_methods_after_clearchat:
                self.custom_methods_after_clearchat.pop(method)

        self.methods_after_clearchat_to_remove = []

    async def _execute_methods_after_delete_message(self, message: Message) -> None:
        tasks = [
            method(message)
            for method in self.custom_methods_after_delete_message.values()
        ]
        await asyncio.gather(*tasks)

    def _remove_methods_after_delete_message(self) -> None:
        for method in self.methods_after_delete_message_to_remove:
            if method in self.custom_methods_after_delete_message:
                self.custom_methods_after_delete_message.pop(method)

        self.methods_after_delete_message_to_remove = []

    async def _execute_methods_after_bot_connected(self, message: Message) -> None:
        tasks = [
            method(message)
            for method in self.custom_methods_after_bot_connected.values()
        ]
        await asyncio.gather(*tasks)

    def _remove_methods_after_bot_connected(self) -> None:
        for method in self.methods_after_bot_connected_to_remove:
            if method in self.custom_methods_after_bot_connected:
                self.custom_methods_after_bot_connected.pop(method)

        self.methods_after_bot_connected_to_remove = []

    async def _execute_methods_after_toggle_host(self, message: Message) -> None:
        tasks = [
            method(message) for method in self.custom_methods_after_toggle_host.values()
        ]
        await asyncio.gather(*tasks)

    def _remove_methods_after_toggle_host(self) -> None:
        for method in self.methods_after_toggle_host_to_remove:
            if method in self.custom_methods_after_toggle_host:
                self.custom_methods_after_toggle_host.pop(method)

        self.methods_after_toggle_host_to_remove = []

    async def _execute_methods_after_server_reconnect(self, message: Message) -> None:
        tasks = [
            method(message)
            for method in self.custom_methods_after_server_reconnect.values()
        ]
        await asyncio.gather(*tasks)

    def _remove_methods_after_server_reconnect(self) -> None:
        for method in self.methods_after_server_reconnect_to_remove:
            if method in self.custom_methods_after_server_reconnect:
                self.custom_methods_after_server_reconnect.pop(method)

        self.methods_after_server_reconnect_to_remove = []

    async def _execute_methods_after_channel_change(self, message: Message) -> None:
        tasks = [
            method(message)
            for method in self.custom_methods_after_channel_change.values()
        ]
        await asyncio.gather(*tasks)

    def _remove_methods_after_channel_change(self) -> None:
        for method in self.methods_after_channel_change_to_remove:
            if method in self.custom_methods_after_channel_change:
                self.custom_methods_after_channel_change.pop(method)

        self.methods_after_channel_change_to_remove = []

    async def _execute_methods_after_event(self, message: Message) -> None:
        tasks = [method(message) for method in self.custom_methods_after_event.values()]
        await asyncio.gather(*tasks)

    def _remove_methods_after_event(self) -> None:
        for method in self.methods_after_event_to_remove:
            if method in self.custom_methods_after_event:
                self.custom_methods_after_event.pop(method)

        self.methods_after_event_to_remove = []

    async def _execute_methods_after_user_join(self, message: Message) -> None:
        tasks = [
            method(message) for method in self.custom_methods_after_user_join.values()
        ]
        await asyncio.gather(*tasks)

    def _remove_methods_after_user_join(self) -> None:
        for method in self.methods_after_user_join_to_remove:
            if method in self.custom_methods_after_user_join:
                self.custom_methods_after_user_join.pop(method)

        self.methods_after_user_join_to_remove = []

    async def _execute_methods_after_whisper(self, message: Message) -> None:
        tasks = [
            method(message) for method in self.custom_methods_after_whisper.values()
        ]
        await asyncio.gather(*tasks)

    def _remove_methods_after_whisper(self) -> None:
        for method in self.methods_after_whisper_to_remove:
            if method in self.custom_methods_after_whisper:
                self.custom_methods_after_whisper.pop(method)

        self.methods_after_whisper_to_remove = []

    def _handle_notice(self, message: Message) -> None:
        logger.info(
            "%s > [%s]: %s | %s",
            message.irc_command,
            message.channel,
            message.text,
            message.irc_tags,
        )

    async def _handle_part(self, message: Message) -> None:
        logger.info("%s > [%s] %s", message.irc_command, message.channel, message.user)

        await self._execute_methods_after_leave_channel(
            message.channel if message.channel is not None else ""
        )
        self._remove_methods_after_leave_channel()

    def _handle_ping(self, message: Message) -> None:
        logger.info("%s > :%s", message.irc_command, message.text)

        self._send_pong(message.text if message.text is not None else "")

    async def _handle_privmsg(self, message: Message) -> None:
        logger.info(
            "%s > [%s] %s: %s | %s",
            message.irc_command,
            message.channel,
            message.user,
            message.text,
            message.irc_tags,
        )

        await self._execute_listeners(message)
        self._remove_listeners()

        if message.text_command in self.custom_commands:
            await self._execute_methods_before_commands(message)
            self._remove_methods_before_commands()
            await self._execute_command(message)
            self._remove_commands()
            await self._execute_methods_after_commands(message)
            self._remove_methods_after_commands()

    async def _handle_clearchat(self, message: Message) -> None:
        logger.info(
            "%s > [%s] %s | %s",
            message.irc_command,
            message.channel,
            message.text if message.text is None else "",
            message.irc_tags,
        )

        await self._execute_methods_after_clearchat(message)
        self._remove_methods_after_clearchat()

    async def _handle_clearmsg(self, message: Message) -> None:
        logger.info(
            "%s > [%s]: %s | %s",
            message.irc_command,
            message.channel,
            message.text,
            message.irc_tags,
        )

        await self._execute_methods_after_delete_message(message)
        self._remove_methods_after_delete_message()

    async def _handle_globaluserstate(self, message: Message) -> None:
        logger.info("%s > | %s", message.irc_command, message.irc_tags)

        await self._execute_methods_after_bot_connected(message)
        self._remove_methods_after_bot_connected()

    async def _handle_hosttarget(self, message: Message) -> None:
        logger.info("%s > [%s]: %s", message.irc_command, message.channel, message.text)

        await self._execute_methods_after_toggle_host(message)
        self._remove_methods_after_toggle_host()

    async def _handle_reconnect(self, message: Message) -> None:
        logger.info("%s >", message.irc_command)

        await self._execute_methods_after_server_reconnect(message)
        self._remove_methods_after_server_reconnect()

    async def _handle_roomstate(self, message: Message) -> None:
        logger.info(
            "%s > [%s] | %s", message.irc_command, message.channel, message.irc_tags
        )

        await self._execute_methods_after_channel_change(message)
        self._remove_methods_after_channel_change()

    async def _handle_usernotice(self, message: Message) -> None:
        logger.info(
            "%s > [%s]: %s | %s",
            message.irc_command,
            message.channel,
            message.text if message.text is not None else "",
            message.irc_tags,
        )

        await self._execute_methods_after_event(message)
        self._remove_methods_after_event()

    async def _handle_userstate(self, message: Message) -> None:
        logger.info(
            "%s > [%s] | %s", message.irc_command, message.channel, message.irc_tags
        )

        await self._execute_methods_after_user_join(message)
        self._remove_methods_after_user_join()

    async def _handle_whisper(self, message: Message) -> None:
        logger.info(
            "%s > %s: %s",
            message.irc_command,
            message.irc_args[0] if message.irc_args is not None else "",
            message.text,
        )

        await self._execute_methods_after_whisper(message)
        self._remove_methods_after_whisper()

    async def _handle_message(self, received_msg: str) -> None:
        if len(received_msg) == 0:
            return

        message = self._parse_message(received_msg)

        if message.irc_command == "NOTICE":
            self._handle_notice(message)

        elif message.irc_command == "PART":
            await self._handle_part(message)

        elif message.irc_command == "PING":
            self._handle_ping(message)

        elif message.irc_command == "PRIVMSG":
            await self._handle_privmsg(message)

        elif message.irc_command == "CLEARCHAT":
            await self._handle_clearchat(message)

        elif message.irc_command == "CLEARMSG":
            await self._handle_clearmsg(message)

        elif message.irc_command == "GLOBALUSERSTATE":
            await self._handle_globaluserstate(message)

        elif message.irc_command == "HOSTTARGET":
            await self._handle_hosttarget(message)

        elif message.irc_command == "RECONNECT":
            await self._handle_reconnect(message)

        elif message.irc_command == "ROOMSTATE":
            await self._handle_roomstate(message)

        elif message.irc_command == "USERNOTICE":
            await self._handle_usernotice(message)

        elif message.irc_command == "USERSTATE":
            await self._handle_userstate(message)

        elif message.irc_command == "WHISPER":
            await self._handle_whisper(message)

        else:
            logger.info(
                "%s > [%s] %s: %s",
                message.irc_command,
                message.channel,
                message.user,
                message.text,
            )

    async def _loop(self) -> None:
        while not self._finish:
            try:
                received_msgs = self.irc.recv(2048).decode()

                for received_msg in received_msgs.split("\r\n"):
                    await self._handle_message(received_msg)

            except socket.timeout:
                await self._execute_checks()
                self._remove_checks()

    def send(self, channel: str, text: str) -> None:
        """
        Sends a message by chat

        Args:
            channel (str): Owner of the chat
            text (str): Message's text
        """

        self._send_privmsg(channel, text)

    def reply(self, channel: str, message_id: str, text: str) -> None:
        """
        Replies to a message in a chat

        Args:
            channel (str): Owner of the chat
            message_id (str): ID of the message being replied to
            text (str): Message's text
        """

        self._send_privmsg(channel, text, message_id)

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
