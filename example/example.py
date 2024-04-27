from datetime import datetime

from twitchpy.bot import Bot

bot = Bot(
    "your_oauth_token",
    "your_client_id",
    "your_client_secret",
    "your_redirect_uri",
    "tokens_file_path",
    "login_of_your_bot",
    ["channels_list_to_read_from"],
    "!",
)

time = datetime.now()


def example_check():
    global time

    time_diff = datetime.now() - time

    if time_diff.seconds >= 5:
        bot.me("any_channel_login", "This message is sent every 5 seconds")
        time = datetime.now()


def example_listener(message):
    if message.user is not None:
        bot.me("any_channel_login", f"{message.user} said: {message.text}")


def example_command(message):
    bot.me("any_channel_login", f"{message.user} is who called me")


bot.add_check("example_check", example_check)
bot.add_listener("example_listener", example_listener)
bot.add_command("example_command", example_command)

bot.run()
