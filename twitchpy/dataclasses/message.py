class Message:
    """
    Represents a message
    """

    def __init__(
        self,
        prefix,
        user,
        channel,
        irc_command,
        irc_args,
        text,
        text_command,
        text_args,
    ):
        """
        Args:
            prefix (str): Message's prefix
            user (str): User who has sent the message
            channel (str): Channel on which the message was sent
            irc_command (str): IRC command related to the message
            irc_args (str): IRC command's arguments
            text (str): Message's text
            text_command (str): Command related to the message
            text_args (str): Command's arguments
        """

        self.prefix = prefix
        self.user = user
        self.channel = channel
        self.irc_command = irc_command
        self.irc_args = irc_args
        self.text = text
        self.text_command = text_command
        self.text_args = text_args
