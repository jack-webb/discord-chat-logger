import sys
from datetime import datetime
import discord
import logging
from babel.dates import format_timedelta

import config
from logger import data, models
from logger.models import MessageContent

intents = discord.Intents.default()
intents.members = True

client = discord.Client(intents=intents)
logging.basicConfig(level=logging.DEBUG)


@client.event
async def on_ready():
    print("=====================")
    print("Discord Chat Logger, by Jack Webb")
    print("https://github.com/jack-webb/discord-chat-logger/")
    print(f"Python version {sys.version}")
    print(f"discord.py version {discord.__version__}")
    print(f"Logger ready, logged in as {client.user}")
    print("=====================")


# todo Nickname/user updates
@client.event
async def on_message(message: discord.Message):
    data.log_message(message)

    if str(message.channel.id) == config.log_channel and message.content[0] == config.prefix:
        _, channel_id, *optional_args = message.content.split(" ")
        if channel_id[0].isdigit():
            error("Embedded channel required, not ID")
        channel_id = channel_id[2:-1]  # Hacky way of removing "<#...>" todo can we get this from the object instead of the str repr

        if len(optional_args) > 1:
            # too many args
            pass
        if len(optional_args) == 1:
            # Should be a date arg, todo validate
            date = datetime.strptime(optional_args[0], '%Y-%m-%d').date()
            messages = data.get_messages_from_channel(channel_id, date)  # todo this is hit twice?
        else:
            messages = data.get_messages_from_channel(channel_id)
            for message in messages:
                print(process_message_out(message))


@client.event
async def on_message_edit(_, message: discord.Message):
    data.log_message(message)


@client.event
async def on_member_update(before: discord.Member, after: discord.Member):
    if before.display_name != after.display_name \
            or before.name != after.name \
            or before.discriminator != after.discriminator:
        data.update_user(after)


# todo this is spitting out a shitload of queries - investigate
def process_message_out(message: models.Message):
    output = ""

    ordered_contents = message.content.order_by(MessageContent.timestamp.desc())
    current, previous = ordered_contents[0], ordered_contents[1:]

    if str(message.author.nickname) == f"{message.author.username}#{message.author.discriminator}":
        output += f"[{message.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {message.author.username}#{message.author.discriminator}: {current.text} {current.attachment_url}"
    else:
        output += f"[{message.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {message.author.username}#{message.author.discriminator} ({message.author.nickname}): {current.text} {current.attachment_url}"

    for content in previous:
        relative_time = current.timestamp - content.timestamp
        output += f"\n↪ {format_timedelta(relative_time, locale='en_US')} ago: {content.text} {content.attachment_url}"

    return output


def error(message: str):
    # Send some error message
    pass


if __name__ == '__main__':
    data.setup_database()
    client.run(config.token)
