# TwitchPy

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-green.svg)](https://github.com/DaCasBe/TwitchPy/blob/master/LICENSE)
[![Formatter: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Pypi downloads](https://img.shields.io/pypi/dm/twitchpy?color=blue)](https://pypi.org/project/twitchpy)

TwitchPy is a Python package for using the Twitch's API and create bots for interacting with their IRC chats.

## Documentation

Click [here](https://dacasbe.github.io/TwitchPy/) to see the official documentation.

## Installation

TwitchPy requires Python 3.10 or higher. You can download the latest version of Python [here](https://www.python.org/downloads/).

~~~
pip install twitchpy
~~~

## Getting started

A basic bot.

~~~```python
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
~~~

## Contributing

TwitchPy currently uses the Black formatter to enforce sensible style formatting.

Before creating a pull request it is encouraged you install and run black on your code.

The line length limit for TwitchPy is 88.

For installation and usage of Black visit: [Black Formatter](https://black.readthedocs.io/en/stable/usage_and_configuration/)

For integrating Black into your IDE visit: [Black IDE Usage](https://black.readthedocs.io/en/stable/integrations/editors.html)

## Contact

You can contact me through my [e-mail](mailto:dacasbe97@gmail.com).